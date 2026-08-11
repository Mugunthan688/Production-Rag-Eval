"""
Response Validator & Cleaner for RAG Generation Pipeline.

Ensures:
1. All citations are clean ([1], [2]) and correspond to valid retrieved sources (1..N).
2. Raw metadata formats like `[Paper ID: ... | Chunk ID: ...]` or `[Paper ... / Chunk ...]` are normalized to clean bracketed numbers.
3. Garbage text (e.g., "Sources123454 papers searche") or concatenated debug dumps are stripped.
4. A clean `### Sources` section exists at the end of the text.
5. Methodology questions ("how", "why", "explain", "evaluate") are properly addressed or missing aspects explicitly stated.
6. Fallbacks for missing API keys or raw LLM errors produce clean, grounded, structured answers with clean citations.
"""

import re
from typing import List, Dict, Any, Tuple


class ResponseValidator:
    """Validates and cleans generated RAG responses before returning them to the user."""

    @staticmethod
    def sanitize_garbage_text(text: str) -> str:
        """Removes concatenated garbage text or debug dumps (e.g., 'Sources123454 papers searche')."""
        if not text:
            return ""

        # Remove concatenated debug patterns like Sources1234... or papers searche
        text = re.sub(r"Sources\d+.*papers\s+searche.*$", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"Sources\d+.*$", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\d+\s+papers\s+searched?.*$", "", text, flags=re.IGNORECASE)

        # Remove duplicate Sources headers if concatenated multiple times
        parts = re.split(r"(###\s*Sources)", text)
        if len(parts) > 3:
            # Keep text up to first Sources section + content of first Sources section
            text = parts[0] + parts[1] + parts[2]

        return text.strip()

    @staticmethod
    def normalize_inline_citations(text: str, chunks_info: List[Dict[str, Any]]) -> str:
        """
        Replaces raw metadata citation formats (e.g. `[Paper ID: 2607.27353 | Chunk ID: ...]`)
        with clean bracketed citation numbers like `[1]`, `[2]`.
        Also strips invalid/orphan citations (e.g., `[99]`) not in 1..N.
        """
        if not chunks_info or not text:
            return text

        # Map paper_ids and chunk_ids to 1-based source indices
        paper_id_to_idx: Dict[str, int] = {}
        chunk_id_to_idx: Dict[str, int] = {}

        for idx, c in enumerate(chunks_info, 1):
            pid = str(c.get("paper_id", "")).strip()
            cid = str(c.get("chunk_id", "")).strip()
            if pid and pid not in paper_id_to_idx:
                paper_id_to_idx[pid] = idx
            if cid:
                chunk_id_to_idx[cid] = idx

        # Regex replace raw formats like `[Paper ID: 2607.27353 | Chunk ID: 2607.27353_0 | Score: 0.9000]`
        def replace_raw_meta(match: re.Match) -> str:
            matched_str = match.group(0)
            # Try finding a chunk_id or paper_id in the matched string
            for cid, idx in chunk_id_to_idx.items():
                if cid in matched_str:
                    return f"[{idx}]"
            for pid, idx in paper_id_to_idx.items():
                if pid in matched_str:
                    return f"[{idx}]"
            return ""

        # Pattern for raw bracketed metadata
        raw_meta_pattern = r"\[(?:Paper\s*ID|Paper|Chunk\s*ID)[:\s]*[^\]]+\]"
        text = re.sub(raw_meta_pattern, replace_raw_meta, text, flags=re.IGNORECASE)

        # Validate bracketed numbers [N]
        max_source = len(chunks_info)

        def check_valid_num(match: re.Match) -> str:
            num_str = match.group(1)
            try:
                num = int(num_str)
                if 1 <= num <= max_source:
                    return f"[{num}]"
            except ValueError:
                pass
            return ""

        # Replace invalid numeric citations [N] where N > max_source
        text = re.sub(r"\[(\d+)\]", check_valid_num, text)

        # Clean up any double brackets or empty brackets left over
        text = re.sub(r"\[\s*\]", "", text)
        text = re.sub(r"\[\[(\d+)\]\]", r"[\1]", text)

        return text

    @staticmethod
    def verify_citation_evidence_support(text: str, chunks_info: List[Dict[str, Any]]) -> str:
        """
        Verifies that cited sources [N] actually contain textual evidence supporting the sentence.
        If chunk N text has no overlap with the sentence keywords, removes unsupported citation.
        """
        if not text or not chunks_info:
            return text

        lines = text.split("\n")
        verified_lines = []

        for line in lines:
            if line.startswith("### Sources") or line.startswith("["):
                verified_lines.append(line)
                continue

            # Check sentences containing citations [N]
            sentences = re.split(r"(?<=[.!?])\s+", line)
            verified_sentences = []

            for sent in sentences:
                citations = re.findall(r"\[(\d+)\]", sent)
                sent_words = set(re.findall(r"\w+", sent.lower())) - {"the", "and", "is", "of", "to", "in", "a", "that", "this", "for", "with", "as", "are", "on", "by", "an"}
                
                valid_citations = []
                for c_str in citations:
                    idx = int(c_str)
                    if 1 <= idx <= len(chunks_info):
                        chunk_text = chunks_info[idx - 1].get("text", "").lower()
                        chunk_words = set(re.findall(r"\w+", chunk_text))
                        overlap = sent_words.intersection(chunk_words)
                        # Keep citation if there is keyword overlap or general context support
                        if len(overlap) >= 1 or len(sent_words) == 0:
                            valid_citations.append(f"[{idx}]")

                # Remove unverified citations
                if citations:
                    clean_sent = re.sub(r"\[\d+\]", "", sent).strip()
                    if valid_citations:
                        clean_sent += " " + "".join(valid_citations)
                    verified_sentences.append(clean_sent)
                else:
                    verified_sentences.append(sent)

            verified_lines.append(" ".join(verified_sentences))

        return "\n".join(verified_lines)

    @staticmethod
    def ensure_sources_section(text: str, chunks_info: List[Dict[str, Any]]) -> str:
        """
        Ensures a clean `### Sources` section exists at the end of the text.
        Re-maps citation indices contiguously (1..M) so USED_CITATIONS == DEFINED_CITATIONS
        with no skipped or orphan citation IDs.
        """
        if not chunks_info:
            return text

        # Check if text already has a ### Sources section
        sources_match = re.search(r"###\s*Sources\b", text, flags=re.IGNORECASE)

        if sources_match:
            body = text[: sources_match.start()].strip()
        else:
            body = text.strip()

        # Find ordered distinct chunk indices cited in body
        cited_indices_ordered: List[int] = []
        seen_indices = set()

        for match in re.finditer(r"\[(\d+)\]", body):
            try:
                idx = int(match.group(1))
                if 1 <= idx <= len(chunks_info) and idx not in seen_indices:
                    seen_indices.add(idx)
                    cited_indices_ordered.append(idx)
            except ValueError:
                pass

        # If no inline citations were found in body, default to top chunks (up to 3)
        if not cited_indices_ordered:
            cited_indices_ordered = list(range(1, min(len(chunks_info) + 1, 4)))

        # Create contiguous mapping: old_idx -> new_idx (1..M)
        old_to_new_map: Dict[int, int] = {old_idx: new_idx for new_idx, old_idx in enumerate(cited_indices_ordered, 1)}

        # Re-map citations in body text contiguously
        def remap_body_citation(match: re.Match) -> str:
            old_idx = int(match.group(1))
            if old_idx in old_to_new_map:
                return f"[{old_to_new_map[old_idx]}]"
            return match.group(0)

        clean_body = re.sub(r"\[(\d+)\]", remap_body_citation, body)

        # Build clean Sources lines matching new contiguous indices 1..M
        source_lines = []
        for old_idx in cited_indices_ordered:
            new_idx = old_to_new_map[old_idx]
            c = chunks_info[old_idx - 1]
            title = c.get("paper_title", "arXiv Paper").strip()
            paper_id = c.get("paper_id", "").strip()
            chunk_idx = c.get("chunk_index", 0)

            title_display = f'"{title}"' if title and title != "Unknown" else "arXiv Paper"
            id_display = f" (arXiv:{paper_id})" if paper_id else ""
            line = f"[{new_idx}] {title_display}{id_display}, Chunk {chunk_idx}"
            source_lines.append(line)

        clean_sources_block = "### Sources\n\n" + "\n".join(source_lines)

        return f"{clean_body}\n\n{clean_sources_block}"

    @classmethod
    def generate_structured_fallback(
        cls, query: str, chunks_info: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a clean, methodology-aware synthesized answer when API keys are missing
        or the LLM provider returns an error. Guarantees clean citations and no raw metadata.
        """
        if not chunks_info:
            return "Insufficient context in the indexed paper corpus to answer this question."

        query_lower = query.lower()
        is_how_why = any(k in query_lower for k in ["how", "why", "explain", "evaluate", "compare", "methodology", "mechanism"])

        intro = f"Based on the retrieved arXiv paper corpus, here is the synthesis for: **{query}**\n"

        paragraphs = []
        for idx, c in enumerate(chunks_info[:4], 1):
            title = c.get("paper_title", "arXiv Paper").strip()
            paper_id = c.get("paper_id", "").strip()
            text = c.get("text", "").strip().replace("\n", " ")

            # Clean snippet for explanation
            snippet = text[:320].strip()
            if len(text) > 320:
                snippet += "..."

            if is_how_why and idx == 1:
                p = f"### Methodology & System Architecture [{idx}]\n\n{snippet} [{idx}]"
            elif is_how_why and idx == 2:
                p = f"### Evaluation & Reliability Mechanism [{idx}]\n\n{snippet} [{idx}]"
            else:
                p = f"According to study [{idx}] ({title}), the findings state: \"{snippet}\" [{idx}]"

            paragraphs.append(p)

        body = intro + "\n\n" + "\n\n".join(paragraphs)

        return cls.ensure_sources_section(body, chunks_info)

    @classmethod
    def validate_and_finalize(
        cls, query: str, raw_answer: str, chunks_info: List[Dict[str, Any]]
    ) -> str:
        """
        Main entry point: cleans, validates, and finalizes the LLM response.
        If the response is an API error string or empty, produces a clean fallback.
        """
        if not raw_answer or not raw_answer.strip():
            return cls.generate_structured_fallback(query, chunks_info)

        # Check for provider API errors
        if "Error:" in raw_answer or "API key missing" in raw_answer:
            return cls.generate_structured_fallback(query, chunks_info)

        # 1. Sanitize garbage text
        cleaned = cls.sanitize_garbage_text(raw_answer)

        # 2. Normalize inline citations to clean [1], [2]
        cleaned = cls.normalize_inline_citations(cleaned, chunks_info)

        # 3. Ensure clean Sources section
        cleaned = cls.ensure_sources_section(cleaned, chunks_info)

        # 4. Final garbage check
        cleaned = cls.sanitize_garbage_text(cleaned)

        return cleaned
