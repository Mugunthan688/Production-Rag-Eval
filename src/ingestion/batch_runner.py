import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Set
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.ingestion.arxiv_client import ArxivClient
from src.ingestion.paper_selector import PaperSelector, TOPIC_PRIORITIES, PRIMARY_FOUNDATIONAL_PAPERS
from src.ingestion.pipeline import IngestionPipeline
from src.db.models import PaperORM, ChunkORM
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.getcwd(), "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "ingestion_progress.json")
REPORT_FILE = os.path.join(DATA_DIR, "corpus_report.json")


class BatchRunner:
    """Resumable Batch Ingestion Engine for 2,000+ Research Paper Corpus."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session
        self.arxiv_client = ArxivClient()
        self.pipeline = IngestionPipeline(db_session)
        os.makedirs(DATA_DIR, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}. Starting fresh.")

        return {
            "completed_queries": [],
            "ingested_paper_ids": [],
            "total_papers": 0,
            "total_chunks": 0,
            "topic_counts": {t: 0 for t in TOPIC_PRIORITIES},
            "last_updated": datetime.now().isoformat(),
        }

    def _save_state(self):
        self.state["last_updated"] = datetime.now().isoformat()
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    async def run_batch_ingestion(self, target_total: int = 2000) -> Dict[str, Any]:
        logger.info(f"=== Starting Resumable Batch Ingestion (Target: {target_total} papers) ===")
        
        # 1. First fetch primary foundational papers explicitly to guarantee primary source coverage
        logger.info("Fetching primary foundational research papers...")
        primary_ids = list(PRIMARY_FOUNDATIONAL_PAPERS.keys())
        for pid in primary_ids:
            if pid in self.state["ingested_paper_ids"]:
                continue
            try:
                # Query by ID directly
                q = f"id:{pid}"
                papers = self.arxiv_client.fetch_papers(search_query=q, max_results=1)
                if papers:
                    p = papers[0]
                    # Upsert and chunk paper
                    chunks_added = await self._ingest_single_paper(p, "Advanced RAG")
                    self.state["ingested_paper_ids"].append(pid)
                    self.state["total_papers"] += 1
                    self.state["total_chunks"] += chunks_added
                    self.state["topic_counts"]["Advanced RAG"] += 1
                    logger.info(f"✅ Primary Paper Ingested: {p.id} - {p.title[:60]}")
            except Exception as e:
                logger.error(f"Error fetching primary paper {pid}: {e}")

        # 2. Iterate across Topic Priorities and query sets
        total_queries = sum(len(info["queries"]) for info in TOPIC_PRIORITIES.values())
        curr_query_idx = 0

        for topic, info in TOPIC_PRIORITIES.items():
            quota = int(target_total * info["quota_ratio"])
            logger.info(f"\n--- Topic: {topic} (Quota: {quota} papers) ---")

            for query_str in info["queries"]:
                curr_query_idx += 1
                if query_str in self.state["completed_queries"]:
                    logger.info(f"Skipping already completed query: '{query_str}'")
                    continue

                if self.state["topic_counts"][topic] >= quota:
                    logger.info(f"Quota reached for topic '{topic}'. Skipping query.")
                    self.state["completed_queries"].append(query_str)
                    self._save_state()
                    continue

                logger.info(f"[{curr_query_idx}/{total_queries}] Executing arXiv search: '{query_str}'")
                try:
                    # Fetch candidates
                    raw_papers = self.arxiv_client.fetch_papers(search_query=query_str, max_results=200)
                    ranked = PaperSelector.deduplicate_and_rank(raw_papers, topic)
                    
                    ingested_count = 0
                    for paper, score in ranked:
                        clean_id = paper.id.split("v")[0]
                        if clean_id in self.state["ingested_paper_ids"]:
                            continue

                        chunks_added = await self._ingest_single_paper(paper, topic)
                        self.state["ingested_paper_ids"].append(clean_id)
                        self.state["total_papers"] += 1
                        self.state["total_chunks"] += chunks_added
                        self.state["topic_counts"][topic] += 1
                        ingested_count += 1

                        if self.state["topic_counts"][topic] >= quota:
                            break

                    logger.info(f"Completed query '{query_str}': Ingested {ingested_count} new papers.")
                    self.state["completed_queries"].append(query_str)
                    self._save_state()
                    await asyncio.sleep(1) # API rate safety
                except Exception as e:
                    logger.error(f"Error in batch query '{query_str}': {e}")

        # 3. Generate Corpus Report
        return await self.generate_corpus_report()

    async def _ingest_single_paper(self, paper: Any, topic: str) -> int:
        paper_orm = PaperORM(
            id=paper.id.split("v")[0],
            title=paper.title,
            abstract=paper.abstract,
            authors=paper.authors,
            categories=paper.categories,
            submitted_date=paper.submitted_date,
            pdf_url=paper.pdf_url,
            full_text=paper.full_text or paper.abstract,
        )
        await self.pipeline.paper_repo.upsert_paper(paper_orm)

        # Delete existing chunks for this paper to ensure idempotency
        await self.pipeline.chunk_repo.delete_chunks_by_strategy(paper_orm.id, "recursive")

        chunks = self.pipeline.chunker.chunk_paper(paper)
        if chunks:
            chunk_texts = [c.text for c in chunks]
            embeddings = self.pipeline.embedder.embed_documents(chunk_texts)
            for c, emb in zip(chunks, embeddings):
                c.embedding = emb

            chunk_orms = [
                ChunkORM(
                    id=f"{paper_orm.id}_chunk_{idx}",
                    paper_id=paper_orm.id,
                    chunk_index=idx,
                    text=c.text,
                    chunking_strategy=c.chunking_strategy,
                    embedding=c.embedding,
                    metadata_json={"topic": topic, "chunk_index": idx, "paper_id": paper_orm.id},
                )
                for idx, c in enumerate(chunks)
            ]
            await self.pipeline.chunk_repo.save_chunks(chunk_orms)
            return len(chunk_orms)
        return 0

    async def generate_corpus_report(self) -> Dict[str, Any]:
        """Generates comprehensive corpus metrics report saved to data/corpus_report.json."""
        p_res = await self.session.execute(select(func.count(PaperORM.id)))
        total_papers = p_res.scalar() or 0

        c_res = await self.session.execute(select(func.count(ChunkORM.id)))
        total_chunks = c_res.scalar() or 0

        report = {
            "total_papers": total_papers,
            "total_chunks": total_chunks,
            "topic_distribution": self.state.get("topic_counts", {}),
            "primary_sources_covered": len(PRIMARY_FOUNDATIONAL_PAPERS),
            "last_updated": datetime.now().isoformat(),
        }

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Corpus Report Generated: Total Papers = {total_papers}, Total Chunks = {total_chunks}")
        return report
