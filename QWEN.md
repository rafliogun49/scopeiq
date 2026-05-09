# ScopeIQ — Project Context

## Project Overview

**ScopeIQ** is an AI-agent-powered idea-validation tool for indie founders. Users describe a product idea in plain English, and within ~5 minutes receive a Markdown research report covering competitor pricing, user complaints from HN/Stack Exchange/Indie Hackers, and gap analysis — all with clickable citations. After the run, users can chat with the collected research via RAG.

**Tech Stack:**
- **Backend:** FastAPI, Python 3.11, SQLModel, PostgreSQL + pgvector, Celery + Redis
- **AI/Agents:** OpenAI Agents SDK (4 agents: Orchestrator, Scraper, Social, Synthesizer), MCP server
- **Frontend:** React 18, TypeScript, TanStack (Router/Query/Form), Tailwind CSS
- **Observability:** Langfuse Cloud
- **Deployment:** Docker Compose on Jetorbit VPS (Ubuntu 24.04)

**Project Type:** Bootcamp final assignment (Devscale AI-Enabled Python Web Development) — 3-person team, 2-week sprint

## Directory Structure

```
scopeiq/
├── backend/              # Python/FastAPI backend
│   ├── app/
│   │   ├── agents/       # 4 AI agents (Orchestrator, Scraper, Social, Synthesizer)
│   │   ├── api/          # REST endpoints (auth, projects, runs, chat)
│   │   ├── core/         # Config, security
│   │   ├── models/       # SQLModel tables (User, Project, Run, RunEvent, Chunk, ChatMessage)
│   │   ├── rag/          # RAG pipeline (chunking, embedding, indexing, retrieval)
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── tools/        # Agent tools (http_fetch, extract_text, tavily, hn, stackexchange)
│   │   └── workers/      # Celery worker setup
│   ├── mcp_server/       # MCP server (python_exec, rag_query tools)
│   ├── evals/            # Evaluation dataset and runner
│   ├── tests/            # pytest tests
│   ├── alembic/          # DB migrations
│   ├── pyproject.toml    # Dependencies (uv)
│   ├── Dockerfile        # Backend container
│   └── Dockerfile.mcp    # MCP server container
├── frontend/             # React/TypeScript frontend
│   ├── src/
│   │   ├── routes/       # TanStack Router file-based routes
│   │   ├── components/   # Reusable UI components
│   │   ├── hooks/        # React hooks
│   │   └── lib/          # API client, SSE, query keys
│   ├── package.json      # Dependencies (pnpm)
│   └── Dockerfile        # Dev + prod build containers
├── deploy/               # VPS deployment scripts
│   ├── setup-vps.sh      # Initial VPS bootstrap
│   └── Caddyfile         # Reverse proxy config
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production deployment
├── PRD.md                      # Full product requirements (1483 lines)
├── TEAM_SPLIT.md               # Team task assignments, interface contracts
└── .env.example                # Environment variable template
```

## Building and Running

### Prerequisites
- Docker Desktop (or `docker` + `docker compose` plugin)
- Python 3.11+ with [uv](https://docs.astral.sh/uv/) — `pip install uv`
- Node 20+ with [pnpm](https://pnpm.io/) — `npm install -g pnpm`

### Quickstart (Docker Compose — Recommended)

```bash
# Clone and setup
git clone https://github.com/<your-team>/scopeiq.git
cd scopeiq
cp .env.example .env
# Edit .env — add your API keys (OPENAI_API_KEY, TAVILY_API_KEY, LANGFUSE_*)

# Start all services
docker compose up --build
```

**Access points:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local Development (Without Docker)

**Backend:**
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
pnpm install
pnpm dev
```

### Running Tests

```bash
cd backend
uv run pytest
```

### Linting and Type Checking

**Backend:**
```bash
cd backend
uv run ruff check .
uv run mypy app
```

**Frontend:**
```bash
cd frontend
pnpm lint
pnpm typecheck
```

## Key Architecture Concepts

### Agent System (4 Agents via OpenAI Agents SDK)

| Agent | Model | Responsibility |
|-------|-------|----------------|
| **Orchestrator** | gpt-4o-mini | Plans runs, dispatches sub-agents, calls `python_exec` tool |
| **Scraper** | gpt-4o-mini | Fetches competitor landing/pricing pages |
| **Social** | gpt-4o-mini | Mines HN, Stack Exchange, Tavily for user complaints |
| **Synthesizer** | gpt-4o | Writes final 4-section Markdown report |

### RAG Pipeline
1. Raw text → chunked (800 tokens, 100 overlap)
2. Chunks → embedded (`text-embedding-3-small`, 1536-dim)
3. Embeddings → stored in pgvector with `ivfflat` index
4. Chat queries → retrieve top-k chunks → LLM answers with citations

### MCP Server
Hosts two tools accessible via MCP protocol:
- `python_exec` — sandboxed Python execution (`unshare -n`, 30s timeout, 256MB cap)
- `rag_query` — wrapper around RAG retrieval

### SSE Event Streaming
Backend emits server-sent events for live run progress:
- Event types: `plan`, `agent_started`, `tool_called`, `agent_finished`, `error`, `log`
- Contract defined in `backend/app/schemas/events.py` and `frontend/src/lib/sse.ts`

## Environment Variables

See `.env.example` for full list. Key variables:

```bash
# API Keys (required)
OPENAI_API_KEY=
TAVILY_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=

# Database
DATABASE_URL=postgresql+psycopg://scopeiq:changeme@db:5432/scopeiq
REDIS_URL=redis://redis:6379/0

# Auth
JWT_SECRET=change-me-in-prod-use-openssl-rand-hex-32

# MCP
MCP_SERVER_URL=http://mcp:7000
```

## Deployment

Production deployment via Docker Compose on Jetorbit VPS:

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec fastapi alembic upgrade head
```

See `PRD.md §23` and `deploy/setup-vps.sh` for full VPS setup.

## Development Conventions

### Code Style
- **Backend:** Ruff linting (E, F, I, UP, B, SIM), MyPy type checking, 100 char line length
- **Frontend:** ESLint (React hooks, refresh), TypeScript strict mode, Prettier formatting

### AI Agent Design (Taste Skills)

This project uses [Taste Skill](https://www.tasteskill.dev/) — an anti-slop frontend framework for AI agents — to ensure premium, non-generic UI output.

**Installed Skills** (`.agents/skills/`):
| Skill | Purpose |
|-------|---------|
| `design-taste-frontend` | Default UI/UX engineering directives (Variance: 8, Motion: 6, Density: 4) |
| `high-end-visual-design` | Awwwards-tier agency design with haptic micro-aesthetics |
| `stitch-design-taste` | Google Stitch semantic design system generation |

**Key Design Rules:**
- **Fonts:** `Geist`, `Satoshi`, `Cabinet Grotesk` (Inter is BANNED for premium contexts)
- **Colors:** Neutral bases (Zinc/Slate) with max 1 accent; AI Purple/Blue neon is BANNED
- **Layouts:** Asymmetric, offset grids; centered hero sections are BANNED for Variance > 4
- **Motion:** Framer Motion with spring physics (`stiffness: 100, damping: 20`); no linear easing
- **Icons:** Phosphor Icons or Radix Icons with consistent `strokeWidth: 1.5` or `2.0`
- **Mobile:** Use `min-h-[100dvh]` (NOT `h-screen`) for full-height sections
- **No Emojis:** Replaced with high-quality icon primitives

**For AI Agents:** When generating frontend code, always load and follow the directives in `.agents/skills/design-taste-frontend/SKILL.md`.

### CI/CD (GitHub Actions)
On every PR:
- Backend: lint, typecheck, tests
- Frontend: build, typecheck
- Docker: build all images

### Definition of Done
- Code merged via PR (never direct to `main`)
- 1 approval from non-author
- CI green
- Tests added/updated
- Acceptance criteria checked off

## Key Documentation

| File | Purpose |
|------|---------|
| `PRD.md` | Full product requirements, system architecture, API spec, sprint plan |
| `TEAM_SPLIT.md` | Team task assignments, interface contracts, day-by-day timeline |
| `README.md` | Quick start guide |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template with acceptance criteria checklist |

## Project Status

**Current State:** Active development — 2-week bootcamp sprint

**Team Structure:** 3 members
- **Member A:** Backend/Agents (FastAPI auth, Orchestrator, Scraper, Celery)
- **Member B:** AI/RAG (RAG pipeline, MCP server, Social, Synthesizer, evals)
- **Member C:** Frontend/DevOps (React app, SSE, Docker, CI/CD, VPS deploy)

**Key Deadlines:**
- Week 1: Vertical slice (signup → run → events stream)
- Week 2: Full system + production deploy + demo
