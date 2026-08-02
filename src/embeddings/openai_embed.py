import logging
from typing import List
from openai import OpenAI

from src.embeddings.base import BaseEmbeddingProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model: str = settings.EMBEDDING_MODEL, api_key: str | None = settings.OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if not self.client:
            logger.warning("OpenAI API key missing, returning zero embeddings mock for development.")
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]

        response = self.client.embeddings.create(input=texts, model=self.model)
        return [data.embedding for data in response.data]

    def embed_query(self, text: str) -> List[float]:
        if not self.client:
            return [0.0] * settings.EMBEDDING_DIMENSION
        response = self.client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding
