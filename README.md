<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<h1 align="center">⚡ Production-Grade RAG System</h1>

<p align="center">
  <b>End-to-end Retrieval-Augmented Generation over arXiv AI Research Papers</b><br>
  <i>Hybrid Search · Neural Reranking · Controlled Evaluation · Glassmorphic Dashboard</i>
</p>

<p align="center">
  <a href="#-key-features">Features</a> •
  <a href="#%EF%B8%8F-system-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-project-structure">Project Structure</a> •
  <a href="#-evaluation-pipeline">Evaluation</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-dashboard">Dashboard</a>
</p>

---

## 🎯 Overview

This is a **production-quality Retrieval-Augmented Generation system** engineered beyond typical tutorial-level RAG projects. It indexes hundreds of arXiv AI/ML research papers and enables complex research question-answering through a multi-stage retrieval pipeline with measurable, reproducible evaluation metrics.

**What makes it production-grade:**
- 🔀 **Hybrid retrieval** — Dense vector search + BM25 sparse search fused via Reciprocal Rank Fusion (RRF)
- 🧠 **Neural reranking** — Cross-Encoder (`ms-marco-MiniLM`) reranker for precision-first candidate scoring
- 📐 **Controlled experiments** — YAML-driven experiment configs with automated metric collection
- 🛡️ **Safety guardrails** — Adversarial prompt injection defense and system prompt leak prevention
- 📊 **Quantitative evaluation** — Precision@K, MRR, Faithfulness, Relevance, and p50/p95 latency tracking

---

## 🚀 Key Features

### 📥 Data Ingestion Pipeline
| Capability | Details |
|---|---|
| **Data Source** | arXiv API (CS.AI, CS.CL, CS.LG categories) — 300+ papers on RAG & LLM Agents |
| **Chunking Strategies** | 3 swappable strategies via Factory Pattern — `Fixed-Size`, `Recursive`, `Semantic` |
| **Embedding Models** | Local `BAAI/bge-small-en-v1.5` (384d) or OpenAI `text-embedding-3-small` |
| **Storage** | PostgreSQL + pgvector for hybrid vector/relational storage |

### 🔍 Multi-Stage Retrieval Pipeline
```
User Query
    │
    ▼
┌─────────────────────┐
│  LLM Query Rewriter │  ← Decompose complex queries into sub-queries
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐ ┌────────┐
│ Dense  │ │ BM25   │  ← Parallel dual-channel retrieval
│ Vector │ │ Sparse │
└───┬────┘ └───┬────┘
    └─────┬─────┘
          ▼
┌─────────────────────┐
│  Reciprocal Rank    │  ← Score-level fusion (RRF k=60)
│  Fusion (RRF)       │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Cross-Encoder      │  ← Neural reranking (ms-marco-MiniLM)
│  Reranker           │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  LLM Answer         │  ← Grounded generation with citations
│  Generation         │
└─────────────────────┘
```

### 🤖 LLM Generation Layer
- **Multi-provider support** — Google Gemini, OpenAI GPT-4, Anthropic Claude via pluggable `BaseLLMProvider` abstraction
- **Grounded answers** — System prompts enforce citation of source chunks and "insufficient context" responses when evidence is weak
- **Prompt templates** — Modular template system for answer synthesis and query rewriting

### 📊 Controlled Evaluation Framework
- **YAML-driven experiments** — Define pipeline configurations as reproducible experiment files
- **Retrieval metrics** — Precision@K, Recall@K, Mean Reciprocal Rank (MRR)
- **Generation metrics** — Faithfulness (LLM-as-judge), Answer Relevance scoring
- **Operational metrics** — p50 / p95 latency, total query cost tracking
- **Side-by-side comparison** — `baseline` vs `full_pipeline` with tabular diff view

### 🛡️ Safety & Guardrails
- Adversarial prompt injection test suite (`data/adversarial_set.json`)
- System prompt leak prevention evaluation
- Input sanitization and response validation

### 💬 Human Feedback Loop
- Thumbs up/down rating collection per query
- Feedback analytics dashboard with lowest-rated query tracking
- Problematic chunk identification for corpus quality improvement

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  ┌──────────────────┐          ┌──────────────────────────┐     │
│  │  Streamlit        │          │  REST API Consumers      │     │
│  │  Dashboard        │ ◄──────► │  (curl / httpx / etc.)   │     │
│  │  (Port 8501)      │          │                          │     │
│  └──────────────────┘          └──────────────────────────┘     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    FastAPI Server    │
                    │    (Port 8000)       │
                    │  ┌───────────────┐   │
                    │  │ /query        │   │
                    │  │ /ingest       │   │
                    │  │ /feedback     │   │
                    │  │ /eval         │   │
                    │  │ /health       │   │
                    │  └───────────────┘   │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼───────┐   ┌─────────▼────────┐   ┌─────────▼────────┐
│  Retrieval     │   │  Generation      │   │  Evaluation      │
│  Pipeline      │   │  Pipeline        │   │  Framework       │
│                │   │                  │   │                  │
│ • Vector Store │   │ • LLM Provider   │   │ • Experiment     │
│ • BM25 Store   │   │   Factory        │   │   Runner         │
│ • RRF Fusion   │   │ • Prompt Engine  │   │ • Metric Suite   │
│ • Reranker     │   │ • Guardrails     │   │ • Comparator     │
│ • Query Rewrite│   │                  │   │                  │
└───────┬───────┘   └──────────────────┘   └──────────────────┘
        │
┌───────▼─────────────────────────────┐
│        PostgreSQL + pgvector        │
│  • papers  • chunks  • embeddings   │
│  • feedback_entries                 │
└─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **API Framework** | FastAPI + Uvicorn (async) |
| **Database** | PostgreSQL 16 + pgvector extension |
| **ORM** | SQLAlchemy 2.0 (async) + Alembic migrations |
| **Embeddings** | Sentence-Transformers (`bge-small-en-v1.5`) / OpenAI |
| **Sparse Search** | rank-bm25 |
| **Reranker** | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) |
| **LLM Providers** | Google Gemini · OpenAI GPT-4 · Anthropic Claude |
| **Evaluation** | Custom metric suite (Precision, MRR, Faithfulness, Latency) |
| **Dashboard** | Streamlit with glassmorphic UI theme |
| **Config** | Pydantic Settings + YAML experiment configs |
| **Containerization** | Docker + Docker Compose |

---

## 📁 Project Structure

```
RAG Application/
├── config/
│   ├── settings.py                  # Pydantic settings (env-driven)
│   ├── logging.yaml                 # Structured logging config
│   └── experiments/                 # YAML experiment definitions
│       ├── baseline.yaml            #   Dense-only, no reranker
│       ├── hybrid_search.yaml       #   Dense + BM25 with RRF
│       ├── reranker_on.yaml         #   Hybrid + Cross-Encoder
│       └── full_pipeline.yaml       #   All features enabled
│
├── src/
│   ├── api/                         # FastAPI application layer
│   │   ├── main.py                  #   App factory + lifespan
│   │   ├── middleware.py            #   Latency logging middleware
│   │   └── routes/                  #   Modular route handlers
│   │       ├── query.py             #     POST /query
│   │       ├── ingest.py            #     POST /ingest
│   │       ├── feedback.py          #     POST & GET /feedback
│   │       ├── eval.py              #     POST /eval
│   │       └── health.py            #     GET /health
│   │
│   ├── ingestion/                   # Data ingestion pipeline
│   │   ├── arxiv_client.py          #   arXiv API fetcher
│   │   ├── pipeline.py              #   Orchestrates fetch → chunk → embed → store
│   │   ├── enrichment.py            #   Metadata enrichment
│   │   └── chunking/                #   Strategy Pattern chunkers
│   │       ├── factory.py           #     Chunker factory
│   │       ├── fixed.py             #     Fixed-size chunking
│   │       ├── recursive.py         #     Recursive text splitter
│   │       └── semantic.py          #     Embedding-based semantic chunking
│   │
│   ├── retrieval/                   # Multi-stage retrieval engine
│   │   ├── pipeline.py              #   Orchestrates full retrieval flow
│   │   ├── vector_store.py          #   pgvector dense search
│   │   ├── bm25_store.py            #   BM25 sparse search
│   │   ├── hybrid.py                #   Reciprocal Rank Fusion
│   │   ├── reranker.py              #   Cross-Encoder neural reranker
│   │   └── query_rewriter.py        #   LLM-powered query decomposition
│   │
│   ├── generation/                  # Answer generation layer
│   │   ├── llm_provider.py          #   Multi-provider LLM factory
│   │   ├── generator.py             #   RAG answer synthesizer
│   │   ├── pipeline.py              #   Generation orchestrator
│   │   └── prompt_templates.py      #   System & user prompt templates
│   │
│   ├── evaluation/                  # Evaluation & benchmarking
│   │   ├── experiment_runner.py     #   YAML-driven experiment executor
│   │   ├── comparator.py           #   Side-by-side result comparator
│   │   └── metrics/                 #   Metric computation modules
│   │       ├── retrieval.py         #     Precision@K, Recall@K, MRR
│   │       ├── generation.py        #     Faithfulness, Relevance (LLM-as-judge)
│   │       └── operational.py       #     Latency p50/p95
│   │
│   ├── embeddings/                  # Embedding provider abstraction
│   ├── feedback/                    # User feedback collection
│   ├── guardrails/                  # Adversarial defense layer
│   └── db/                          # Database models & engine
│
├── dashboard/                       # Streamlit analytics UI
│   ├── app.py                       #   Main dashboard entry point
│   ├── components/
│   │   ├── styles.py                #   Glassmorphic theme engine
│   │   ├── chunk_viewer.py          #   Interactive chunk inspector
│   │   └── metrics_table.py         #   Experiment comparison renderer
│   └── pages/
│       ├── 01_query.py              #   Interactive Query Inspector
│       ├── 02_experiments.py        #   Experiment Benchmark Matrix
│       ├── 03_feedback.py           #   Feedback Analytics
│       └── 04_adversarial.py        #   Security Guardrails
│
├── scripts/                         # CLI utilities
│   ├── fetch_arxiv.py               #   Standalone arXiv paper fetcher
│   ├── run_ingestion.py             #   Full ingestion pipeline runner
│   ├── run_eval.py                  #   Experiment evaluation runner
│   └── seed_db.py                   #   Database initialization
│
├── tests/                           # Test suite
│   ├── unit/                        #   Unit tests
│   ├── integration/                 #   Integration tests
│   └── adversarial/                 #   Adversarial safety tests
│
├── data/                            # Evaluation & test datasets
│   ├── eval_set.json                #   Ground-truth evaluation queries
│   ├── eval_set_schema.json         #   Evaluation set schema definition
│   └── adversarial_set.json         #   Prompt injection test cases
│
├── alembic/                         # Database migrations
├── docker-compose.yml               # Full stack orchestration
├── Dockerfile                       # API server container
├── Dockerfile.streamlit             # Dashboard container
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── pyproject.toml                   # Project metadata & tool config
└── .env.example                     # Environment variable template
```

---

## ⚡ Getting Started

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 16** with [pgvector](https://github.com/pgvector/pgvector) extension
- **Docker & Docker Compose** *(optional — for containerized setup)*
- At least one LLM API key: **Google Gemini** (free tier available), **OpenAI**, or **Anthropic**

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Mugunthan688/Production-Rag-Eval.git
cd rag-application

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API key(s)

# 3. Launch the full stack
docker-compose up --build
```

> 🟢 **API Server** → `http://localhost:8000` &nbsp;|&nbsp; 📊 **Dashboard** → `http://localhost:8501` &nbsp;|&nbsp; 📝 **API Docs** → `http://localhost:8000/docs`

### Option 2: Local Development

```bash
# 1. Clone and set up virtual environment
git clone https://github.com/Mugunthan688/Production-Rag-Eval.git
cd rag-application
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Configure environment
cp .env.example .env
# Edit .env — at minimum, set GEMINI_API_KEY or OPENAI_API_KEY

# 4. Initialize database & ingest papers
python scripts/seed_db.py
python scripts/run_ingestion.py --max-results 200

# 5. Start the API server
uvicorn src.api.main:app --reload --port 8000

# 6. Start the dashboard (new terminal)
streamlit run dashboard/app.py --server.port 8501
```

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ (or another LLM key) | — | Google Gemini API key |
| `OPENAI_API_KEY` | Optional | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | Optional | — | Anthropic API key |
| `DATABASE_URL` | For Postgres | SQLite fallback | PostgreSQL connection string |
| `EMBEDDING_PROVIDER` | No | `local` | `local` (BGE) or `openai` |
| `LLM_PROVIDER` | No | `gemini` | `gemini`, `openai`, or `anthropic` |
| `HYBRID_SEARCH_ENABLED` | No | `true` | Enable BM25 + Vector fusion |
| `RERANKER_ENABLED` | No | `true` | Enable Cross-Encoder reranking |
| `QUERY_REWRITING_ENABLED` | No | `true` | Enable LLM query decomposition |

---

## 📊 Evaluation Pipeline

### Running Experiments

Experiments are defined as YAML configs in `config/experiments/`:

```yaml
# config/experiments/full_pipeline.yaml
experiment_name: full_pipeline
chunking_strategy: semantic
chunk_size: 500
chunk_overlap: 50
hybrid_search: true
reranker: true
query_rewriting: true
top_k_retrieval: 20
top_k_rerank: 5
```

```bash
# Run a single experiment
python scripts/run_eval.py --config config/experiments/baseline.yaml

# Run all experiments for comparison
python scripts/run_eval.py --config config/experiments/full_pipeline.yaml
```

### Experiment Configurations

| Experiment | Chunking | Hybrid Search | Reranker | Query Rewriting |
|---|---|---|---|---|
| `baseline` | Fixed | ❌ | ❌ | ❌ |
| `hybrid_search` | Recursive | ✅ | ❌ | ❌ |
| `reranker_on` | Recursive | ✅ | ✅ | ❌ |
| `full_pipeline` | Semantic | ✅ | ✅ | ✅ |

### Metrics Tracked

| Category | Metrics |
|---|---|
| **Retrieval Quality** | Precision@K, Recall@K, Mean Reciprocal Rank (MRR) |
| **Generation Quality** | Faithfulness Score, Answer Relevance (LLM-as-judge) |
| **Operational** | p50 Latency, p95 Latency, Total Query Cost |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check and system status |
| `POST` | `/query` | Execute RAG pipeline — retrieve, rerank, generate |
| `POST` | `/ingest` | Trigger paper ingestion from arXiv |
| `POST` | `/feedback` | Submit user rating for a query result |
| `GET` | `/feedback/analytics` | Retrieve feedback analytics summary |
| `POST` | `/eval` | Run evaluation experiment |

### Example Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What retrieval methods reduce hallucination in long-context RAG?",
    "chunking_strategy": "recursive",
    "hybrid_search": true,
    "reranker": true,
    "query_rewriting": true
  }'
```

Full interactive API documentation available at **`http://localhost:8000/docs`** (Swagger UI).

---

## 🖥️ Dashboard

The Streamlit dashboard features a custom **"Deep Research AI"** glassmorphic dark theme:

| Page | Description |
|---|---|
| **🏠 Home** | System overview with pipeline metrics (corpus status, retrieval mode, reranker model, LLM provider) |
| **🔍 Query Inspector** | Interactive RAG pipeline — enter questions, inspect reranked chunks, view generated answers with latency badges |
| **📊 Experiments** | Side-by-side benchmark comparison matrix across all experiment configurations |
| **💬 Feedback** | User rating analytics — lowest-rated queries and problematic chunk identification |
| **🛡️ Guardrails** | Adversarial prompt injection and system prompt leak test case viewer |

### Theme Design

- **Color palette** — Indigo (`#6366F1`) → Purple (`#A855F7`) → Pink (`#EC4899`) gradient spectrum
- **Glassmorphic cards** — `backdrop-filter: blur(12px)` with hover-lift transitions
- **Typography** — Inter (body) + Plus Jakarta Sans (headings) from Google Fonts
- **Dark canvas** — Deep navy (`#090D16`) with subtle radial gradient overlays

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run adversarial safety tests
pytest tests/adversarial/ -v

# Run all tests with coverage
pytest --cov=src tests/ -v
```

---

## 🐳 Docker

```bash
# Build and run full stack
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f dashboard

# Tear down
docker-compose down -v
```

**Services:**
| Container | Image | Port |
|---|---|---|
| `rag_postgres` | `pgvector/pgvector:pg16` | `5432` |
| `rag_api` | Custom (Dockerfile) | `8000` |
| `rag_dashboard` | Custom (Dockerfile.streamlit) | `8501` |

---

## 📌 Design Decisions

| Decision | Rationale |
|---|---|
| **Hybrid Search (RRF)** | Dense vectors miss lexical matches; BM25 misses semantic similarity. RRF fusion captures both without learned weights. |
| **Cross-Encoder Reranker** | Bi-encoder retrieval is fast but shallow. Cross-encoder attention over `(query, passage)` pairs dramatically improves precision in the top-K. |
| **Strategy Pattern for Chunking** | Enables controlled A/B experiments — swap chunking strategies without touching retrieval or generation code. |
| **LLM Provider Factory** | Decouples the system from any single vendor. Switch between Gemini/OpenAI/Claude via a single env variable. |
| **YAML Experiment Configs** | Reproducibility-first design — every experiment run is fully defined by a declarative config file. |
| **SQLite Fallback** | Local development works without PostgreSQL — the system auto-falls back to SQLite for rapid prototyping. |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Built with ❤️ for AI Research</b><br>
  <i>If you found this project useful, consider giving it a ⭐</i>
</p>
