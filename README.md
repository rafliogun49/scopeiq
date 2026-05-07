# ScopeIQ

> "Should I build this? Get the answer in 5 minutes."

ScopeIQ is an AI-agent-powered idea-validation tool for indie founders. Type a product idea; ~5 minutes later get a Markdown research report covering competitor pricing, user complaints from HN + Stack Exchange + Indie Hackers, and a gap analysis — all with clickable citations. After the run, chat with the collected research via RAG.

Built with FastAPI · OpenAI Agents SDK · pgvector · MCP · React/TanStack · Celery · Docker.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or `docker` + `docker compose` plugin)
- Python 3.11+ with [uv](https://docs.astral.sh/uv/) — `pip install uv`
- Node 20+ with [pnpm](https://pnpm.io/) — `npm install -g pnpm`

---

## Quickstart (Docker Compose)

```bash
git clone https://github.com/<your-team>/scopeiq.git
cd scopeiq
cp .env.example .env
# Edit .env — paste your OpenAI, Tavily, and Langfuse keys
nano .env

docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Local development (without Docker)

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

---

## Running tests

```bash
cd backend
uv run pytest
```

---

## Project docs

- [`PRD.md`](PRD.md) — full product requirements (what & why)
- [`TEAM_SPLIT.md`](TEAM_SPLIT.md) — who owns what, PR list, interface contracts

---

## Deployment

See [PRD §23 — VPS Deployment (Jetorbit)](PRD.md#23-vps-deployment-jetorbit) and the scripts in [`deploy/`](deploy/).

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec fastapi alembic upgrade head
```
