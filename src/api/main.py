import os
# Configure single-threaded execution to stay strictly within Render's 512MB RAM limit
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from ..config.settings import settings
from ..db.engine import init_db
from .middleware import LatencyLoggingMiddleware
from .routes import health, query, ingest, eval as eval_route, feedback, papers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas & extensions on startup safely
    try:
        await init_db()
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").warning(f"Database init warning (non-fatal): {e}")
    yield



app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Production-Grade RAG System with Evaluation Pipeline API",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(LatencyLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Production-Grade RAG System API",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }


app.include_router(health.router)
app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(eval_route.router)
app.include_router(feedback.router)
app.include_router(papers.router)
