from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App & Database
    APP_NAME: str = "Production-Grade RAG System"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db"

    # Keys
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    COHERE_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Defaults
    EMBEDDING_PROVIDER: Literal["openai", "local", "gemini"] = "local"

    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LOCAL_EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384


    LLM_PROVIDER: Literal["openai", "anthropic", "gemini", "local"] = "gemini"
    LLM_MODEL: str = "gemini-flash-latest"

    DEFAULT_CHUNKING_STRATEGY: Literal["fixed", "recursive", "semantic"] = "recursive"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    HYBRID_SEARCH_ENABLED: bool = True
    RERANKER_ENABLED: bool = True
    QUERY_REWRITING_ENABLED: bool = True
    TOP_K_RETRIEVAL: int = 20
    TOP_K_RERANK: int = 5


settings = Settings()
