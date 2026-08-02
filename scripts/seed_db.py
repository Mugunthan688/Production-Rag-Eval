import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.engine import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Initializing database tables and extension (pgvector)...")
    await init_db()
    logger.info("Database schema initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
