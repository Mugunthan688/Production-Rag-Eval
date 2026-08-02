import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

AR5IV_BASE_URL = "https://ar5iv.labs.arxiv.org/html"


class Ar5ivEnricher:
    """Stretch goal: fetch HTML full-text from ar5iv for cleaner parsing than raw PDF."""

    def __init__(self, base_url: str = AR5IV_BASE_URL):
        self.base_url = base_url

    def fetch_full_text(self, paper_id: str) -> str | None:
        url = f"{self.base_url}/{paper_id}"
        logger.info(f"Fetching ar5iv HTML full-text from {url}")
        try:
            resp = httpx.get(url, timeout=20.0, follow_redirects=True)
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch ar5iv full-text for {paper_id}, status={resp.status_code}")
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            # Extract main article body text
            article = soup.find("article")
            if article:
                return article.get_text(separator="\n", strip=True)
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error fetching ar5iv full text for {paper_id}: {e}")
            return None
