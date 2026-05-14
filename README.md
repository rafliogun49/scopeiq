# ScopeIQ

> "Should I build this? Get the answer in 5 minutes."

ScopeIQ is an AI-agent-powered idea-validation tool for indie founders. Type a product idea; ~5 minutes later get a Markdown research report covering competitor pricing, user complaints from HN + Stack Exchange + Indie Hackers, and a gap analysis — all with clickable citations. After the run, chat with the collected research via RAG.

Built with FastAPI · OpenAI Agents SDK · pgvector · MCP · React/TanStack · Celery · Docker.

[![CI](https://github.com/rafliogun49/scopeiq/actions/workflows/ci.yml/badge.svg)](https://github.com/rafliogun49/scopeiq/actions/workflows/ci.yml)

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or `docker` + `docker compose` plugin)
- Python 3.11+ with [uv](https://docs.astral.sh/uv/) — `pip install uv`
- Node 20+ with [pnpm](https://pnpm.io/) — `npm install -g pnpm`

---

## Quickstart (Recommended)

### Option 1: Using Makefile (Easiest)

```bash
git clone https://github.com/rafliogun49/scopeiq.git
cd scopeiq
cp .env.example .env
# Edit .env — add your OpenAI, Tavily, and Langfuse keys

make dev  # Start all services
```

**Access points:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Option 2: Using Docker Compose

```bash
git clone https://github.com/rafliogun49/scopeiq.git
cd scopeiq
cp .env.example .env
# Edit .env — add your API keys

docker compose up --build
```

---

## Testing the Frontend (with Mocks)

**No backend needed!** The frontend uses [MSW](https://mswjs.io/) to mock all API endpoints.

### Using Makefile
```bash
make dev  # MSW auto-enabled in development mode
```

### Test Credentials
- **Email:** test@example.com
- **Password:** password123

### Demo Flow
1. Visit http://localhost:5173
2. Sign up or log in
3. View sample projects (2 pre-loaded)
4. Click "Start Research" to see live SSE streaming (~10s)
5. View completed report with citations
6. Chat with research findings

---

## Local Development (without Docker)

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

## Makefile Commands

```bash
# Development
make dev          # Start all services
make stop         # Stop all services
make clean        # Fresh start (deletes volumes)

# Testing & Quality
make test         # Run backend tests (pytest)
make lint         # Run linters (ruff + eslint)
make typecheck    # Run type checkers (mypy + tsc)
make format       # Format code (ruff + prettier)
make precommit    # Run pre-commit hooks

# Database
make migrate      # Run database migrations
make db-shell     # Open psql shell
make logs         # View all logs

# Build & Deploy
make build        # Build Docker images
make deploy       # Deploy to production VPS
```

See full list: `make help`

---

## Running Tests

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Testing
Frontend uses MSW for integration testing. Run the dev server and test manually:
```bash
cd frontend
pnpm dev
# Visit http://localhost:5173
```

---

## CI/CD

GitHub Actions runs on every PR:
- ✅ Backend: lint (ruff), typecheck (mypy), tests (pytest)
- ✅ Frontend: build, typecheck (tsc)
- ✅ Docker: build all images

Pre-commit hooks run locally before each commit:
- ✅ Backend: ruff lint + format
- ✅ Frontend: prettier
- ✅ All: trailing whitespace, end-of-file fixer, YAML check

---

## Project Status

**Current State:** ✅ **Frontend Complete** — Backend in progress

### Completed Frontend Features (Member C)
- ✅ C-PR1: Frontend scaffold (TanStack Router/Query/Form)
- ✅ C-PR2: Local Docker setup (6 services)
- ✅ C-PR3: Auth UI (login/signup)
- ✅ C-PR4: Projects dashboard + create
- ✅ C-PR5: Run progress with SSE streaming
- ✅ C-PR6: Report viewer + Chat interface
- ✅ C-PR6: MSW mocks for all endpoints

### In Progress / Pending
- ⏳ C-PR7: CI/CD pipeline (this PR)
- ⏳ A-PR2: Auth endpoints (Member A)
- ⏳ A-PR3: Projects + Runs CRUD (Member A)
- ⏳ A-PR4: Agent orchestration + SSE (Member A)
- ⏳ B-PR: Report + Chat endpoints (Member B)
- ⏳ C-PR8: VPS deployment (Member C)

---

## Project Docs

| File | Purpose |
|------|---------|
| [`PRD.md`](PRD.md) | Full product requirements |
| [`TEAM_SPLIT.md`](TEAM_SPLIT.md) | Team task assignments |
| [`QWEN.md`](QWEN.md) | Project context |
| [`docs/`](docs/) | Implementation plans |

---

## Deployment

See [PRD §23 — VPS Deployment (Jetorbit)](PRD.md#23-vps-deployment-jetorbit) and the scripts in [`deploy/`](deploy/).

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec fastapi alembic upgrade head
```

Or using Makefile:
```bash
make deploy
```

---

## Contributing

### Development Workflow
1. Create branch from `develop`: `git checkout -b feat/your-feature`
2. Install pre-commit: `pip install pre-commit && pre-commit install`
3. Make changes, pre-commit runs automatically
4. Push and create PR targeting `develop`
5. Get 1 approval from non-author
6. Merge when CI is green

### Commit Convention
- `feat:` New feature
- `fix:` Bug fix
- `chore:` Configuration, dependencies
- `docs:` Documentation
- `test:` Tests
- `ci:` CI/CD configuration

---

## Team

**Member C** — Frontend/DevOps
- React 18 + TypeScript
- TanStack (Router/Query/Form)
- Docker + CI/CD
- VPS deployment

---

## License

MIT
