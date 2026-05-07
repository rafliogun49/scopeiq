# ScopeIQ — Team Task Split

> **Purpose of this document:** so all 3 members have the *same* understanding of who owns what, what each PR contains, and how the pieces hand off to each other. Read it together on Day 0; refer back during the sprint.
>
> Companion to `PRD.md`. The PRD is the *what*; this doc is the *who*.

---

## Table of Contents

1. [At a Glance](#1-at-a-glance)
2. [The 4 Agents — Who Owns Each](#2-the-4-agents--who-owns-each)
3. [Member A — Backend / Agents](#3-member-a--backend--agents)
4. [Member B — AI / RAG](#4-member-b--ai--rag)
5. [Member C — Frontend / DevOps](#5-member-c--frontend--devops)
6. [Tech Lead Role (Adds On Top)](#6-tech-lead-role-adds-on-top)
7. [Interface Contracts (How You Hand Off)](#7-interface-contracts-how-you-hand-off)
8. [Day-by-Day Timeline (Per Person)](#8-day-by-day-timeline-per-person)
9. [Pairing Moments (Don't Skip These)](#9-pairing-moments-dont-skip-these)
10. [Fairness Guardrails](#10-fairness-guardrails)
11. [Definition of Done (Per Ticket)](#11-definition-of-done-per-ticket)
12. [Communication Norms](#12-communication-norms)

---

## 1. At a Glance

| Member | Role | Primary Domains | Approx. PRs |
|---|---|---|---|
| **A** | Backend / Agents | FastAPI auth + project/run CRUD, Orchestrator + Scraper agents, Celery pipeline | 5 |
| **B** | AI / RAG | RAG pipeline, MCP server (`python_exec` + `rag_query`), Social + Synthesizer agents, evals | 5 |
| **C** | Frontend / DevOps | React + TanStack app, SSE consumer, chat UI, Docker, CI/CD, **Jetorbit VPS deployment** | 7 |

**The Tech Lead is one of A/B/C (wears 2 hats), not a 4th person.** Decide who on Day 0.

**Fairness note:** A and B carry roughly equal AI-engineering content; C carries less AI but more breadth (frontend + DevOps + deploy). See [§10](#10-fairness-guardrails) for guardrails.

---

## 2. The 4 Agents — Who Owns Each

The system has **4 LLM agents**. Two are owned by Member A, two by Member B.

| # | Agent | Owner | Job | Tools | Model |
|---|---|---|---|---|---|
| 1 | **Orchestrator** | A | The boss. Plans the run, dispatches Scraper + Social, calls `python_exec` directly, hands off to Synthesizer. | `handoff_to_*`, `python_exec` | gpt-4o-mini |
| 2 | **Scraper** | A | Visits competitor URLs (landing, pricing, about) and extracts text. | `http_fetch`, `extract_text`, `discover_urls` | gpt-4o-mini |
| 3 | **Social** | B | Mines HN, Stack Exchange, and Tavily (Indie Hackers + review domains) for user complaints, alternatives, traction signals, review snippets. | `tavily_search`, `hn_search`, `stackexchange_search` | gpt-4o-mini |
| 4 | **Synthesizer** | B | Writes the final 4-section Markdown report from everything in pgvector. | `rag_query` | **gpt-4o** |

> **Note:** "Coder" is **not** an agent in v3. `python_exec` is a *tool* the Orchestrator calls directly when it has structured pricing data ready to chart.

---

## 3. Member A — Backend / Agents

### A's mental model
You own the **request → response** path on the backend, the **agent runtime**, and the **first two agents**. When something goes wrong with HTTP, auth, the Celery worker, or the Orchestrator/Scraper, A is the on-call.

### A's PR list

#### A-PR1 — `feat/repo-and-fastapi-skeleton` (Day 1, ~4 hr)
- Initialize `backend/` directory per Appendix A of PRD
- `pyproject.toml` (uv or poetry), Python 3.11
- FastAPI `main.py` with `/health` route
- SQLModel base + DB connection (Postgres via `DATABASE_URL`)
- Alembic init + first empty migration
- `app/core/config.py` — pydantic-settings reading `.env`
- **Interface delivered:** working FastAPI server, DB connection, migrations runnable
- **Acceptance:** `docker compose up api db` → `curl localhost:8000/health` returns 200

#### A-PR2 — `feat/auth` (Day 2, ~6 hr)
- `User` SQLModel + migration
- `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`
- bcrypt password hashing
- JWT (HS256, 7-day expiry) via `python-jose`
- `get_current_user` dependency
- pytest tests for signup/login/me/wrong-password
- **Interface delivered:** `Authorization: Bearer <jwt>` works on protected routes
- **Acceptance:** signup → login → call `/auth/me` with token → returns user; tests green

#### A-PR3 — `feat/projects-runs-crud` (Day 3, ~6 hr)
- `Project`, `Run`, `RunEvent` SQLModels + migration
- All endpoints from PRD §15 (Projects + Runs sections, except SSE)
- Celery app setup (`app/workers/celery_app.py`) with Redis broker
- `POST /projects/{id}/runs` enqueues a Celery task (stub task for now — just sets status to `running` then `completed`)
- **Interface delivered:** Member C can create projects + start runs from the UI
- **Acceptance:** can create project + start run end-to-end via curl; run row appears with status transitions

#### A-PR4 — `feat/orchestrator-and-scraper-agents` (Days 4–5, ~10 hr)
- `app/agents/orchestrator.py` — OpenAI Agents SDK agent definition
- `app/agents/scraper.py` — Agents SDK agent
- `app/tools/http_fetch.py` (httpx + robots.txt + per-host rate limit)
- `app/tools/extract_text.py` (trafilatura)
- `app/tools/discover_urls.py` (1-level crawl, cap 5)
- Replace stub Celery task with real Orchestrator → Scraper handoff
- Wire **B's chunking pipeline** (call after Scraper finishes)
- Emit `RunEvent` rows for `plan`, `agent_started`, `tool_called`, `agent_finished`
- **Interface delivered:** running a Run actually fetches a competitor site and emits events
- **Acceptance:** start run for "Notion alternatives" → see Scraper hit 1+ URLs → chunks land in `chunk` table

#### A-PR5 — `feat/celery-resilience-and-budget` (Days 6–8, ~6 hr)
- Tool retry/backoff (2x exponential)
- Per-run hard token cap (100k input / 25k output) — abort with `failed`
- Per-run max tool calls (15 fetches / 8 searches)
- Per-agent max turns (12)
- `Run.cost_usd` updated as agents finish (computed from token counts × model price)
- **Interface delivered:** runaway-cost protection
- **Acceptance:** test that a forced-fail run marks `Run.status='failed'` with reason

### A's "stretch / shared" tasks (do if ahead)
- Help B with Langfuse instrumentation across agents (Day 7)
- Pair with C on the SSE event schema (Day 4)

---

## 4. Member B — AI / RAG

### B's mental model
You own everything that turns **text into knowledge**: chunking, embeddings, vector search, the MCP server (which is the bootcamp's "MCP requirement" box-tick), and the **last two agents**. The Synthesizer is the agent that produces the actual report — its output IS the product.

### B's PR list

#### B-PR1 — `feat/rag-pipeline` (Days 1–2, ~8 hr)
- `app/rag/chunking.py` — token-aware splitter (800 tokens, 100 overlap)
- `app/rag/embedding.py` — OpenAI `text-embedding-3-small` wrapper, batched
- `Chunk` SQLModel + migration with `Vector(1536)` column + `ivfflat` index
- `app/rag/index.py` — `index_chunks(run_id, raw_docs)` per PRD §11
- `app/rag/retrieval.py` — `query(run_id, text, top_k=8)` returning chunks + scores
- pytest covering: chunk boundaries respect tokens, embedding shape is 1536, retrieval returns expected chunk for known fixture
- **Interface delivered:** A's agents can call `index_chunks()` after fetching; chat can call `query()`
- **Acceptance:** unit test inserts 3 fixture docs → query returns the right one in top-1

#### B-PR2 — `feat/mcp-server` (Day 3, ~8 hr)
- `backend/mcp_server/` standalone Python service speaking MCP
- Tool 1: `python_exec(code, dataset_id)` — subprocess sandbox per PRD §13 (`unshare -n`, 30s timeout, 256MB cgroup, whitelisted imports)
- Tool 2: `rag_query(query, run_id, top_k=8)` — wraps B-PR1's retrieval
- `Dockerfile.mcp`
- Smoke-test script: feeds a mock pricing dataset → expects bar chart PNG back
- **Interface delivered:** A's Orchestrator can call `python_exec`; B's Synthesizer can call `rag_query`
- **Acceptance:** `mcp_server` container starts; smoke test produces a valid base64 PNG

#### B-PR3 — `feat/social-agent` (Days 4–5, ~8 hr)
- `app/tools/tavily.py` — Tavily search wrapper, supports `include_domains` and `exclude_domains` (always excludes `reddit.com`); three call patterns — review snippets, Indie Hackers threads, and general market signal
- `app/tools/stackexchange.py` — Stack Exchange API v2.3 wrapper, default sites = `softwarerecs/workplace/startups/stackoverflow`, clear User-Agent
- `app/tools/hn.py` — Algolia HN Search API
- `app/agents/social.py` — Agents SDK agent, prompt directs it to find complaint threads + review snippets
- Wire post-finish chunking (same pattern as Scraper) — collected text → indexed
- Theme classification call: cheap LLM tags each snippet with `pricing | UX | sync | support | missing-feature` (used later by `python_exec` Job 2)
- **Interface delivered:** Orchestrator can hand off to Social and get back chunked, indexed evidence
- **Acceptance:** smoke test on "Notion alternatives" returns ≥10 chunks across HN + Stack Exchange + Tavily-surfaced Indie Hackers

#### B-PR4 — `feat/synthesizer-agent` (Days 6–7, ~10 hr)
- `app/agents/synthesizer.py` — Agents SDK agent on **gpt-4o**
- Prompt template: 4 sections per PRD §6 Epic 4 (Real market? / Who's there / What users hate / Where's the gap)
- Hard rule: every quantitative claim cites `[source: <url>]`
- Embeds the chart PNG produced by Orchestrator's `python_exec` call
- Output: full Markdown saved to `Run.report_md`
- **Interface delivered:** running a Run produces a complete Markdown report
- **Acceptance:** end-to-end run on demo idea produces a 4-section report ≥ 800 words with ≥ 3 citations

#### B-PR5 — `feat/evals` (Days 7–8, ~6 hr)
- `evals/dataset.jsonl` — 10 hand-curated indie-founder ideas with expected competitor count + known pain themes
- `evals/run_eval.py` — runs the system on each, scores via LLM-judge + assertion checks
- Metrics: accuracy, coverage (≥3 competitors), citation density, cost, latency
- **Nightly only** (not on every PR)
- **Interface delivered:** quantitative quality signal for prompt tuning
- **Acceptance:** running `python evals/run_eval.py` on 3 ideas produces a JSON report

### B's "stretch / shared" tasks
- Prompt-tune Synthesizer based on first eval run (Day 8)
- Help A wire `python_exec` from the Orchestrator (Day 4 pairing)

---

## 5. Member C — Frontend / DevOps

### C's mental model
You own everything the user **sees** and everything that gets ScopeIQ **onto a public URL**. You also own CI/CD. Even though you do less direct AI work, you ship the most PRs because frontend + DevOps fans out into many small surfaces.

### C's PR list

#### C-PR1 — `feat/frontend-scaffold-tanstack` (Day 1, ~4 hr)
- `frontend/` Vite + React 18 + TS
- TanStack Router (file-based), TanStack Query, TanStack Form
- Tailwind + shadcn/ui base
- `lib/api.ts` — fetch client, JWT in localStorage, base URL from env
- `lib/qk.ts` — centralized query keys
- Empty home + login routes
- **Acceptance:** `pnpm dev` boots; visiting `/` shows "ScopeIQ" placeholder

#### C-PR2 — `feat/docker-compose-local` (Day 1, parallel with C-PR1, ~3 hr)
- `docker-compose.yml` for local: postgres+pgvector, redis, fastapi, frontend, mcp
- `.env.example` with every var the team needs
- README "getting started" section
- **Acceptance:** new dev clones repo + `docker compose up` → frontend at `:5173`, API at `:8000`

#### C-PR3 — `feat/auth-ui` (Day 2, ~5 hr)
- `/signup`, `/login` routes — TanStack Form
- `_authed/` layout group with auth guard (redirects to `/login` if no token)
- `useMe()` hook (TanStack Query) using `/auth/me`
- Logout button in nav
- **Acceptance:** signup → land on dashboard → refresh keeps session → logout clears

#### C-PR4 — `feat/projects-dashboard-and-create` (Day 3, ~5 hr)
- `/` — list of user's projects (TanStack Query)
- `/projects/new` — TanStack Form (name, idea, optional known_competitors as comma-separated)
- `/projects/:id` — project overview with tabs (Runs / Report / Chat)
- **Acceptance:** create project → see it in dashboard → click → land on overview

#### C-PR5 — `feat/run-progress-sse` (Days 4–5, ~7 hr)
- `/projects/:id/runs/:runId` route
- `useRunStream(runId)` hook — `EventSource` wrapper, accumulates events into a list
- Live timeline: each event renders as a card with agent name, tool, timestamp
- Cumulative cost + token counters at top
- "Cancel run" button (calls `POST /runs/:id/cancel`)
- On `event: complete` → invalidate run query → report appears
- **Acceptance:** start a run → see ≥1 event per agent step stream in within 2s of emission

#### C-PR6 — `feat/report-and-chat-ui` (Days 6–7, ~8 hr)
- `/projects/:id/report` — react-markdown + remark-gfm; citations as `[1]` superscripts; "Download .md" button
- Embedded base64 chart renders inline
- `/projects/:id/chat` — message list + TanStack Form input bar; citation chips below assistant messages
- Hooks: `useMessages`, `useSendMessage` (TanStack Query mutation)
- **Acceptance:** completed run shows readable report with at least one chart; chat round-trip works with citations clickable

#### C-PR7 — `feat/ci-cd` (Day 7, ~3 hr)
- `.github/workflows/ci.yml` — backend lint (ruff) + type (mypy) + tests (pytest); frontend build; docker images build (no push)
- Pre-commit config (ruff + prettier)
- Branch protection on `main`: require PR + 1 approval + CI green (Tech Lead enables in repo settings)
- **Acceptance:** opening any PR runs CI; failing tests block merge

#### C-PR8 — `feat/vps-deploy` (Days 8–9, ~10 hr)
- `docker-compose.prod.yml` per PRD §23.5
- `deploy/Caddyfile` — domain or IP variant per §23.6
- `deploy/setup-vps.sh` — codifies §23.4 bootstrap
- Verify `unshare`/`CAP_SYS_ADMIN` works on Jetorbit (test on Day 0; if blocked, fall back to seccomp+bubblewrap)
- First successful prod deploy with HTTPS working
- README "deployment" section
- **Acceptance:** `https://<vps-ip-or-domain>` serves the app over TLS; demo run works end-to-end on prod

### C's "stretch / shared" tasks
- **Recommended AI ownership for fairness:** the **cost-display widget** in the run page that talks to Langfuse cost data — gives C exposure to the observability stack
- Or: own the `<source>` tag wrapping for prompt-injection defense (cross-cuts both backend prompts and frontend display)
- Pair with A on the SSE event schema (Day 4)

---

## 6. Tech Lead Role (Adds On Top)

The Tech Lead is **one** of A/B/C, plus these extra duties (~4–5 hr/week extra):

- **Holds API keys** — manages 1Password (or similar); never commits keys
- **Owns the demo** — runs the dry-run on Day 9 and the live demo on Day 10
- **Architecture tiebreaker** — when A/B/C disagree on a contract, Tech Lead decides
- **Cost watcher** — exports OpenAI billing weekly; flags overruns in standup
- **Langfuse account owner** — Day 0 setup, dashboard sharing
- **Jetorbit account owner** — billing, SSH root key, addon decisions
- **PR-merge gate** — enforces "1 approval from non-author" rule

> **Recommendation:** Tech Lead = **C**. Why: C owns deploy, which is the riskiest single thing in Week 2. Having the deploy-owner also be the demo-runner removes an entire handoff. Trade-off: C is the most loaded member already, so if C is junior or stretched, **A** is the next-best Tech Lead pick (owns the agent runtime, which is the second-highest-risk area).

---

## 7. Interface Contracts (How You Hand Off)

The 5 places where two members' code meet. Lock these contracts on **Day 2** so nobody is blocked.

### 7.1 A → B: `index_chunks(run_id, raw_docs)`

After A's Scraper or B's Social agent finishes fetching, they pass a list of raw docs to B's indexing function:

```python
# Pydantic schema (lives in app/schemas/rag.py — owned by B)
class RawDoc(BaseModel):
    url: str
    text: str
    source_type: Literal["landing", "pricing", "review_snippet", "community", "hn", "stackexchange"]
    competitor: str | None = None

def index_chunks(run_id: UUID, docs: list[RawDoc]) -> int:
    """Returns number of chunks indexed."""
```

**Lock by:** Day 2 (B writes the schema, A imports it).

### 7.2 A ↔ C: SSE event schema

Both backend and frontend must agree on the JSON shape:

```typescript
// frontend/src/lib/sse.ts — mirrors backend/app/schemas/events.py
type RunEvent = {
  type: "plan" | "agent_started" | "tool_called" | "agent_finished" | "error" | "log";
  agent: string | null;            // e.g. "scraper" | "social" | "orchestrator" | "synthesizer"
  payload: Record<string, unknown>;
  timestamp: string;               // ISO8601
};
```

**Lock by:** Day 3 morning (pair session, A + C, 30 min). Write a fixture JSON both sides import.

### 7.3 A → MCP (B's `python_exec`)

The Orchestrator calls `python_exec` with structured data:

```python
# Tool input
{
  "code": "<python source as string>",
  "dataset_id": "<UUID — corresponds to a JSON blob the orchestrator stashed in Redis>"
}
# Tool output
{
  "stdout": "...",
  "charts": ["<base64 PNG>", ...]  # from plt.savefig
}
```

**Lock by:** Day 3 (B publishes MCP server with mock; A integrates Day 4).

### 7.4 B → MCP (`rag_query`)

The Synthesizer calls `rag_query`:

```python
# Tool input
{ "query": "Notion pricing", "run_id": "<UUID>", "top_k": 8 }
# Tool output
[ { "chunk": "...", "source_url": "...", "score": 0.87 }, ... ]
```

**Lock by:** Day 3 (B owns both ends — internal contract, but document it).

### 7.5 Backend API ↔ Frontend

The full REST API is in PRD §15. C consumes it via `lib/api.ts`. Single contract change rule: **API change = OpenAPI updated = C notified in standup**. FastAPI auto-generates OpenAPI; C uses `openapi-typescript` to regenerate types.

---

## 8. Day-by-Day Timeline (Per Person)

Mirrors PRD §22 but with explicit per-PR mapping.

### Week 1 — Foundations & Vertical Slice

| Day | A | B | C |
|---|---|---|---|
| **0** | Day 0 checklist (all 3 together) | Same | Same + provision Jetorbit + create repo |
| **1** | A-PR1 (FastAPI skeleton) | B-PR1 (RAG pipeline) part 1 | C-PR1 (frontend scaffold) + C-PR2 (docker-compose local) |
| **2** | A-PR2 (auth) | B-PR1 (RAG) finish + lock §7.1 | C-PR3 (auth UI) |
| **3** | A-PR3 (projects/runs CRUD + Celery wiring) | B-PR2 (MCP server) | C-PR4 (projects dashboard) + lock §7.2 SSE schema |
| **4** | A-PR4 part 1: Orchestrator + Scraper agent (mock data) | B-PR3 part 1: Tavily + HN + Stack Exchange tools | C-PR5 part 1: SSE consumer + timeline |
| **5** | **Mid-sprint sync (60 min, all 3).** A-PR4 finish: Scraper end-to-end on 1 competitor | B-PR3 finish: Social agent end-to-end | C-PR5 finish: run page wired; first VPS smoke deploy |

**End of Week 1:** vertical slice — signup → create project → start run → Scraper + Social fetch → chunks indexed → events stream to UI. **No Synthesizer yet.**

### Week 2 — Full System, Deploy, Polish

| Day | A | B | C |
|---|---|---|---|
| **6** | A-PR5 part 1: retry/backoff + per-host rate limit | B-PR4 (Synthesizer) | C-PR6 part 1 (report viewer) |
| **7** | A-PR5 part 2: Langfuse instrumentation across all agents | B-PR5 (evals — start) | C-PR6 finish (chat UI) + C-PR7 (CI/CD) |
| **8** | A-PR5 finish: cost tracking + budget enforcement | B-PR5 finish + prompt tuning from first eval | C-PR8 part 1 (prod docker-compose + Caddyfile) |
| **9** | Bug bash + cache demo run | Bug bash + verify charts render | C-PR8 finish: prod deploy + DNS + HTTPS + bug bash |
| **10** | **Demo dry-run AM → final demo + submission PM** | Same | Same |

---

## 9. Pairing Moments (Don't Skip These)

Three short pairing sessions where two people sit together (call or in person, 30–60 min each). They cost an hour and save a day.

| When | Who | Topic | Why |
|---|---|---|---|
| **Day 3 AM** | A + C | SSE event schema | Mismatched event shape = hours of "why isn't the timeline updating" |
| **Day 4 AM** | A + B | Orchestrator ↔ MCP `python_exec` | The Orchestrator's prompt has to know exactly what `python_exec` accepts; easier to align live |
| **Day 5 AM** | All 3 | Mid-sprint integration check | Verify the vertical slice actually slices vertically; rebalance if anyone is drowning |

---

## 10. Fairness Guardrails

The split is roughly balanced by hours, but **not perfectly** balanced by AI content (this is an AI bootcamp). Decide together on Day 0 how to handle this.

### 10.1 Acknowledged imbalance

| Member | Hours of AI/agent code | Hours of non-AI code |
|---|---|---|
| A | ~16 (2 agents + tools + Celery agent runtime) | ~14 (auth, CRUD, infra) |
| B | ~32 (RAG + MCP + 2 agents + evals) | ~0 |
| C | ~3 (cost-display widget — recommended) | ~38 (frontend + DevOps + deploy) |

### 10.2 Three guardrails

1. **Each member ships ≥ 5 PRs from ≥ 2 distinct domains.** Track in pinned doc; check at Day 5 sync.
2. **Each member presents at the demo.** A demos the run timeline; B demos the report + chat; C demos the deploy + GitHub PR/CI dashboard. Bootcamp graders see all 3 contributing.
3. **One AI exposure for C.** Recommended: cost-display widget (talks to Langfuse) **or** prompt-injection defense (`<source>` wrapping). Both are small and give C a foot in the AI half of the codebase.

### 10.3 Mid-sprint rebalance triggers

At the Day 5 sync, rebalance if any of these are true:
- A or B is more than half a day behind on their PR list → C takes evals or report-viewer polish off their hands
- C is more than half a day ahead → C picks up a small AI ticket (e.g. Langfuse instrumentation, owned with B)
- Anyone says "I'm drowning" → reassign immediately, don't wait

---

## 11. Definition of Done (Per Ticket)

A PR is **not** mergeable unless all of these are true:

- [ ] Code merged via PR to `develop` (never directly to `main`)
- [ ] **1 approval from a member who didn't author it**
- [ ] CI green (lint + type-check + tests + frontend build)
- [ ] Tests added/updated for new behavior
- [ ] Docs updated if API or schema changed
- [ ] Acceptance criteria from this doc explicitly checked off in PR description
- [ ] Manually verified end-to-end where the change is user-visible

PR template (put in `.github/PULL_REQUEST_TEMPLATE.md`):

```markdown
## What changed
<bullet list>

## How tested
<commands run, screenshots, logs>

## Acceptance (from TEAM_SPLIT.md)
- [ ] <criterion 1>
- [ ] <criterion 2>

## Screenshots / logs
<if UI or visible behavior>
```

---

## 12. Communication Norms

- **Channel:** one Slack/Discord room for the team. No DMs for project decisions — they get lost.
- **Daily async standup** (10 min, written): *Yesterday / Today / Blockers.* Post by 10am local time.
- **Sync calls:** Day 0 kickoff (2 hr), Day 5 mid-sprint (60 min), Day 9 demo dry-run (60 min). That's it.
- **Blocker rule:** if you're stuck > 2 hours, ping the relevant member. Don't sit on it.
- **Decision log:** any architectural decision goes in `decisions.md` (one-line entry: *Date — Decision — Why*). Tech Lead enforces.
- **Tag conventions in commits/PRs:** `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`. Match recent commit style.

---

*End of TEAM_SPLIT.md — read together on Day 0; refer back anytime work feels uneven or contracts feel unclear.*
