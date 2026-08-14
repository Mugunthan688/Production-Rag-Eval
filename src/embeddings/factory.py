from src.embeddings.base import BaseEmbeddingProvider
from src.embeddings.openai_embed import OpenAIEmbeddingProvider
from src.embeddings.local_embed import LocalEmbeddingProvider
from src.embeddings.gemini_embed import GeminiEmbeddingProvider
from config.settings import settings


def get_embedding_provider(provider_type: str = settings.EMBEDDING_PROVIDER) -> BaseEmbeddingProvider:
    provider_lower = provider_type.lower()
    if provider_lower == "openai":
        return OpenAIEmbeddingProvider()
    elif provider_lower == "gemini":
        return GeminiEmbeddingProvider()
    elif provider_lower == "local":
        return LocalEmbeddingProvider()
    else:
        return LocalEmbeddingProvider()


