import os
import logging
import httpx
from typing import List
from src.embeddings.base import BaseEmbeddingProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini REST API Embedding Provider (Zero PyTorch RAM footprint, instant cloud execution)."""

    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
        self.api_key = key.strip() if key else None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        if not text or not self.api_key or "YOUR_" in self.api_key:
            return [0.0] * 768
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{self.model_name}",
            "content": {"parts": [{"text": text}]}
        }
        try:
            resp = httpx.post(url, json=payload, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("embedding", {}).get("values", [0.0] * 768)
            logger.warning(f"Gemini embedding API returned HTTP {resp.status_code}: {resp.text}")
            return [0.0] * 768
        except Exception as e:
            logger.error(f"Gemini query embedding request failed: {e}")
            return [0.0] * 768
