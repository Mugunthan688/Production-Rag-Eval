from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config.settings import settings
from ..db.engine import init_db
from .middleware import LatencyLoggingMiddleware
from .routes import health, query, ingest, eval as eval_route, feedback, papers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas & extensions on startup
    await init_db()
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
    allow_origins=["*", "http://localhost:5173", "http://localhost:8501"],
    allow_credentials=True,
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
