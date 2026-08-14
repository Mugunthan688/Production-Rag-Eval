from src.embeddings.base import BaseEmbeddingProvider
from src.embeddings.openai_embed import OpenAIEmbeddingProvider
from src.embeddings.local_embed import LocalEmbeddingProvider
from src.embeddings.gemini_embed import GeminiEmbeddingProvider
from config.settings import settings


def get_embedding_provider(provider_type: str = settings.EMBEDDING_PROVIDER) -> BaseEmbeddingProvider:
    provider_lower = provider_type.lower()
    
    # Auto-switch to Gemini embeddings if on cloud memory-constrained environment and GEMINI_API_KEY is active
    if provider_lower == "gemini" or (settings.GEMINI_API_KEY and provider_lower == "local"):
        try:
            import psutil
            mem = psutil.virtual_memory()
            if mem.total < 1024 * 1024 * 1024:  # Under 1GB RAM (Render Free Tier 512MB)
                return GeminiEmbeddingProvider()
        except Exception:
            pass

    if provider_lower == "openai":
        return OpenAIEmbeddingProvider()
    elif provider_lower == "gemini":
        return GeminiEmbeddingProvider()
    elif provider_lower == "local":
        return LocalEmbeddingProvider()
    else:
        return LocalEmbeddingProvider()

