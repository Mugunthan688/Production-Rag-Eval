import re
from typing import List, Dict, Any


class GeneralVsSpecificReasoningEngine:
    """
    Enforces distinction between general framework behavior (e.g. general GraphRAG, general Self-RAG)
    and paper-specific variants (e.g. HVM-GraphRAG, ACE-GraphRAG, DocNavRAG).
    """

    KNOWN_SPECIFIC_VARIANTS = {
        "hvm-graphrag": "HVM-GraphRAG (Hierarchical Vector-Memory GraphRAG)",
        "ace-graphrag": "ACE-GraphRAG (Context-Engineered GraphRAG)",
        "docnavrag": "DocNavRAG (Stateful Evidence Assembly)",
        "agent-uct": "Agent-UCT (UCT Workflow Optimization)",
        "rishielrag": "TriShieldRAG (Defense-in-Depth RAG)",
    }

    @classmethod
    def format_reasoning_instructions(cls, query: str) -> str:
        """Returns specific prompt guidance to prevent conflating paper variants with general frameworks."""
        q_lower = query.lower()
        
        guidance = [
            "REASONING & GENERAL-VS-SPECIFIC CONSTRAINTS:",
            "1. DIRECT ANSWER FIRST: Provide a direct 1-2 sentence core answer immediately in the first paragraph.",
            "2. GENERAL FRAMEWORK FIRST: Explain the core, general principles of the concept first before mentioning specific paper variants.",
        ]

        if "graphrag" in q_lower:
            guidance.append(
                "3. GRAPHRAG DISTINCTION: Explain GENERAL GraphRAG principles first (knowledge graph representation, entity/relationship extraction, community summaries). "
                "Do NOT present HVM-GraphRAG, ACE-GraphRAG, or DocNavRAG as general GraphRAG features. "
                "Explicitly attribute paper-specific variants with phrasing like 'One GraphRAG variant, HVM-GraphRAG, proposes...'."
            )
        elif "self-rag" in q_lower:
            guidance.append(
                "3. SELF-RAG DISTINCTION: Explain GENERAL Self-RAG principles first (adaptive retrieval, reflection tokens like IsRel, IsSup, IsUse). "
                "Do NOT present related frameworks like Active RAG or Self-Correcting RAG as equivalent to Self-RAG."
            )
        elif "dualg" in q_lower or "macro-reasoning" in q_lower or "micro-matching" in q_lower:
            guidance.append(
                "3. DUALG-MRAG MECHANISM REQUIREMENTS:\n"
                "   - Start directly: 'DualG-MRAG is a multimodal RAG framework that separates high-level structural reasoning from fine-grained feature matching using two graph tiers.'\n"
                "   - Explain the dual-tier graph structure:\n"
                "     * Macro-reasoning graph: 'What is related to what?' (high-level structural/relational reasoning).\n"
                "     * Micro-matching graph: 'Which specific features/evidence match?' (fine-grained feature matching).\n"
                "   - Explain why decoupling is critical: fine-grained features create graph noise/expansion, while coarse representations lose local evidence.\n"
                "   - Explain the execution flow: GNN encoding -> reasoning path representation -> dynamic programming path extraction -> structured guidance -> LLM/VLM generation."
            )
        elif "knowledge graph" in q_lower or "kg" in q_lower:
            guidance.append(
                "3. KNOWLEDGE GRAPH RAG ENHANCEMENT:\n"
                "   - Explain the core enhancement: explicit entities, relationships, multi-hop connections, and cross-document evidence.\n"
                "   - Contrast Traditional RAG (query -> vector similarity -> chunks) with KG-Enhanced RAG (query -> entities/relations -> graph paths -> supporting evidence).\n"
                "   - Use qualified claims ('can improve', 'particularly useful for multi-hop questions') rather than universal assertions."
            )

        return "\n".join(guidance)

