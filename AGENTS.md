# Repository Guidelines

## Project Structure & Module Organization

ScopeIQ is a Dockerized FastAPI + React application. Backend source lives in `backend/app/`, with API routes in `backend/app/api/`, SQLModel models in `backend/app/models/`, agents in `backend/app/agents/`, RAG code in `backend/app/rag/`, and Celery setup in `backend/app/workers/`. Backend tests live in `backend/tests/`; migrations live in `backend/alembic/`.

Frontend source lives in `frontend/src/`. Routes are under `frontend/src/routes/`, reusable UI and feature components under `frontend/src/components/`, hooks under `frontend/src/hooks/`, and shared API/SSE/query utilities under `frontend/src/lib/`. Deployment files are at the repo root plus `deploy/`.

## Build, Test, and Development Commands

- `docker compose up --build`: start the full local stack: db, redis, api, celery, mcp, and frontend.
- `docker compose exec api alembic upgrade head`: apply backend database migrations.
- `docker compose exec api uv run pytest`: run backend tests.
- `docker compose exec api uv run ruff check .`: lint backend Python.
- `docker compose exec api uv run mypy app`: type-check backend code.
- `docker compose exec frontend pnpm lint`: lint frontend code.
- `docker compose exec frontend pnpm typecheck`: type-check frontend TypeScript.
- `docker compose -f docker-compose.prod.yml up -d --build`: build and start the production stack.

## Coding Style & Naming Conventions

Backend uses Python 3.11, Ruff, MyPy, SQLModel, and FastAPI. Keep route modules focused by resource, use typed function signatures, and prefer Pydantic/SQLModel schemas over untyped dictionaries. Frontend uses React 18, TypeScript strict mode, TanStack Router/Query/Form, and Tailwind CSS. Use centralized query keys from `frontend/src/lib/qk.ts`; do not inline query key arrays. Keep component names in `PascalCase`, hooks as `useX`, and utility files in `camelCase` or existing local style.

## Testing Guidelines

Add or update tests when changing backend behavior, API contracts, RAG logic, or worker flows. Use pytest in `backend/tests/`, with names like `test_auth.py` and functions like `test_login_returns_token`. For frontend work, run lint and TypeScript checks at minimum; add component or integration tests if a test framework is introduced. Verify Docker Compose workflows when touching deployment, env, or service wiring.

## Commit & Pull Request Guidelines

Use concise conventional commit prefixes seen in history: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, and `ci:`. PRs should target `develop`, describe the change, list verification commands, and note any migration, environment, or deployment impact. Include screenshots or short screen recordings for UI changes.

## Security & Configuration Tips

Never commit real API keys or production secrets. Start from `.env.example` and set local values in `.env`. Required services include PostgreSQL + pgvector, Redis, OpenAI, Tavily, Langfuse, and the MCP server. For production, verify `JWT_SECRET`, API keys, Caddy routing, migrations, and MCP sandbox capability before demo testing.

## Agent-Specific Instructions

Follow `QWEN.md` and the docs in `docs/` before making broad changes. Frontend work should respect the installed Taste Skills guidance in `.agents/skills/design-taste-frontend/SKILL.md`. Always ask for confirmation before changing or writing files or code, unless the user has explicitly requested that exact edit. Keep edits scoped to the requested area and avoid unrelated refactors.
