from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from config.settings import settings
from .models import Base

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


import os
import gzip
import shutil
import logging

logger = logging.getLogger(__name__)


async def init_db():
    db_path = "./rag_app.db"
    seed_gz = "data/rag_app_seed.db.gz"

    # Auto-seed database from pre-indexed corpus seed if db file is missing or empty (<10MB)
    if os.path.exists(seed_gz):
        if not os.path.exists(db_path) or os.path.getsize(db_path) < 10 * 1024 * 1024:
            try:
                logger.info(f"Extracting corpus database seed from {seed_gz} to {db_path}...")
                with gzip.open(seed_gz, "rb") as f_in:
                    with open(db_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                logger.info("Corpus database seed extraction complete (2,033 papers / 11,755 chunks ready).")
            except Exception as e:
                logger.error(f"Error seeding database from {seed_gz}: {e}")

    async with engine.begin() as conn:
        if "postgresql" in settings.DATABASE_URL:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
