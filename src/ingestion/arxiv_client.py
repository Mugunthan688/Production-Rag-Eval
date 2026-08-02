import logging
import re
from datetime import datetime
from typing import List, Optional
import xml.etree.ElementTree as ET
import httpx
import feedparser

from .models import PaperMetadata

logger = logging.getLogger(__name__)

ARXIV_API_URL = "https://export.arxiv.org/api/query"


class ArxivClient:
    def __init__(self, base_url: str = ARXIV_API_URL):
        self.base_url = base_url

    def fetch_papers(
        self,
        search_query: str = 'all:"retrieval augmented generation"',
        start: int = 0,
        max_results: int = 200,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> List[PaperMetadata]:
        params = {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        logger.info(f"Fetching arXiv papers with query: '{search_query}', max_results={max_results}")
        
        import time
        max_retries = 4
        for attempt in range(1, max_retries + 1):
            try:
                response = httpx.get(self.base_url, params=params, timeout=120.0, follow_redirects=True)
                response.raise_for_status()
                return self.parse_feed(response.text)
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt == max_retries:
                    logger.error(f"arXiv request failed after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"arXiv API request attempt {attempt} failed ({e}). Retrying in {attempt * 3}s...")
                time.sleep(attempt * 3)

    def parse_feed(self, xml_content: str) -> List[PaperMetadata]:
        feed = feedparser.parse(xml_content)
        papers: List[PaperMetadata] = []

        for entry in feed.entries:
            # Extract paper ID from entry.id (e.g., http://arxiv.org/abs/2312.00001v1 -> 2312.00001)
            raw_id = entry.id.split("/abs/")[-1]
            paper_id = re.sub(r"v\d+$", "", raw_id)

            title = entry.title.replace("\n", " ").strip()
            abstract = entry.summary.replace("\n", " ").strip()

            authors = [author.name for author in entry.get("authors", [])]
            categories = [tag.term for tag in entry.get("tags", [])]

            # Parse date
            published_str = entry.get("published", "")
            try:
                submitted_date = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                submitted_date = datetime.utcnow()

            pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

            papers.append(
                PaperMetadata(
                    id=paper_id,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    categories=categories,
                    submitted_date=submitted_date,
                    pdf_url=pdf_url,
                )
            )

        logger.info(f"Successfully parsed {len(papers)} papers from arXiv feed.")
        return papers
