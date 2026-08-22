# DevAI Hub

> Discover the right AI tools for every developer task.

DevAI Hub is a developer-first, free-first AI tool discovery platform. It is not a list of links:
you can describe a problem in plain language ("I need a free AI tool to generate Java unit tests")
and get explainable recommendations, compare tools side by side, and see exactly what each tool's
free tier actually gives you.

The catalogue ships with **500+ tools** across AI and classic developer tooling
(diagrams/UML, email, slides, spreadsheets, and non-AI utilities such as draw.io),
**45 categories** and curated collections. Most tools offer some form of free access.

---

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quick start](#quick-start)
- [Database setup](#database-setup)
- [Environment variables](#environment-variables)
- [Running the backend](#running-the-backend)
- [Running the frontend](#running-the-frontend)
- [Seeding the database](#seeding-the-database)
- [Running tests](#running-tests)
- [API documentation](#api-documentation)
- [Data honesty rules](#data-honesty-rules)
- [Future roadmap](#future-roadmap)

---

## Features

**Discovery**

- Homepage with featured free tools, popular categories, recently added tools, developer
  favourites and twelve task-based workflows
- Full-text search across names, descriptions, categories, features, technologies, free-access
  wording and best-for statements
- Faceted filters: pricing model, category, technology, feature, platform, integration and
  capability toggles (open source, API, free API, agent, MCP, local models)
- Category pages, curated collections, and SEO landing pages such as `/free-ai-coding-tools`

**Deciding**

- **What do I need?** — describe a task, pick a budget, get a ranked list with the reasons for
  each match and a breakdown of how your request was interpreted
- **Build my stack** — answer five questions, get one pick per job across ten areas
- **Compare** — up to four tools side by side across pricing, capabilities, developer support and
  fit, with unknown values shown as unknown rather than as "no"
- **Free tools** — grouped by *how* they are free: completely free, open source, generous free
  tiers, free credits, free developer APIs

**Personal, without an account**

- Favourites and recently viewed tools, stored in `localStorage`
- A comparison shortlist that follows you across pages
- Shareable URLs: every filter, search and comparison is in the address bar

**Honesty by design**

- Seven standardised pricing states: `FREE_FOREVER`, `FREE_TIER`, `FREE_CREDITS`, `FREE_TRIAL`,
  `OPEN_SOURCE`, `BYOK`, `PAID_ONLY` — a trial is never displayed as "free"
- Structured free-access grants (amount, unit, period, restrictions, credit card, expiry)
- Prices stored as structured plans with a verification date and the provider URL they came from
- A transparent record-completeness score with every component shown; no invented "9.8/10" ratings
- No fabricated popularity numbers — "Developer favorites" stays hidden until real people save
  tools

---

## Architecture

```text
                    React Frontend
                           |
                           v
                    FastAPI Backend
                           |
             +-------------+-------------+
             v             v             v
         Tool API      Search API   Recommendation API
             |             |             |
             +-------------+-------------+
                           v
                      Service Layer
                           |
                           v
                    Repository Layer
                           |
                           v
                  PostgreSQL / SQLite
```

Route handlers only validate and delegate. Business logic lives in services; all SQL lives in
repositories. Presentation rules (how a price or a free tier is worded) live in
`app/utils/presentation.py` so the API, the cards and the comparison table can never disagree.

Search adapts to the database it is given: PostgreSQL full-text search with a GIN index when
available, and a portable `LIKE`-based scorer on SQLite, behind one repository method.

---

## Tech stack

| Layer     | Choice                                                                |
| --------- | --------------------------------------------------------------------- |
| Backend   | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x (async), Alembic     |
| Database  | PostgreSQL 16 (asyncpg); SQLite (aiosqlite) for zero-setup local dev   |
| Frontend  | React 18, TypeScript, Vite 6, Tailwind CSS 3, TanStack Query, React Router |
| Testing   | pytest, pytest-asyncio, httpx                                          |

---

## Project structure

```text
devai-hub/
├── backend/
│   ├── app/
│   │   ├── main.py                 # app factory, CORS, error handlers, lifespan
│   │   ├── api/
│   │   │   ├── deps.py             # service injection
│   │   │   └── routes/             # tools, categories, search, recommendations,
│   │   │                           # compare, collections, favorites, discover, admin
│   │   ├── core/                   # config, enums, errors, pagination, security
│   │   ├── db/                     # engine, session, declarative base
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── repositories/           # all SQL
│   │   ├── services/               # business logic + intent extraction + scoring
│   │   │   ├── llm/                # optional LLM provider interface (not required)
│   │   │   └── discovery/          # scaffolding for future automated discovery
│   │   ├── utils/                  # text, presentation, quality scoring
│   │   └── seed/                   # JSON dataset + idempotent seeder
│   ├── alembic/                    # migrations
│   ├── tests/                      # 80 tests
│   ├── scripts/smoke.py            # end-to-end endpoint smoke test
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/             # layout, tools, search, compare, ui
│       ├── pages/                  # 13 routes
│       ├── hooks/                  # theme, filters, favourites, debounce, meta tags
│       ├── services/               # typed API client
│       ├── types/                  # API types mirroring the Pydantic schemas
│       └── utils/                  # formatting and localStorage helpers
├── start.ps1                       # one-command local start (Windows)
├── start.bat
└── README.md
```

---

## Quick start

From the repo root, one command starts everything (installs deps if needed, seeds SQLite, runs API + UI):

```powershell
.\start.ps1
# or double-click start.bat
```

Then open <http://localhost:5173>. API docs: <http://localhost:8000/docs>.

### Manual (two terminals)

```bash
# 1. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env
python -m app.seed                # 500+ tools
uvicorn app.main:app --reload --port 8000

# 2. Frontend (second terminal)
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to port 8000, so there is no CORS setup in development.

---

## Database setup

**SQLite (default).** `DATABASE_URL=sqlite+aiosqlite:///./devai_hub.db`. The schema is created
automatically at startup. Nothing else to do.

**PostgreSQL (recommended for anything real).** It unlocks real full-text search ranking and the
GIN indexes in the migration.

```bash
createdb devai_hub
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/devai_hub

cd backend
alembic upgrade head
python -m app.seed
```

Alembic owns the PostgreSQL schema; the app never creates tables implicitly there.

---

## Environment variables

Copy `backend/.env.example` to `backend/.env`. Nothing is required for local development.

| Variable                | Default                                | Purpose                                        |
| ----------------------- | -------------------------------------- | ---------------------------------------------- |
| `DATABASE_URL`          | `sqlite+aiosqlite:///./devai_hub.db`   | Async SQLAlchemy URL                           |
| `CORS_ORIGINS`          | `http://localhost:5173`                | Comma-separated allowed origins                |
| `ADMIN_API_KEY`         | unset                                  | Enables the admin API; while unset it returns 401 |
| `ENVIRONMENT`           | `development`                          | `development` / `test` / `staging` / `production` |
| `LOG_LEVEL`             | `INFO`                                 | `DEBUG` makes the SQLite driver very chatty    |
| `DEFAULT_PAGE_SIZE`     | `24`                                   | Page size when the client does not ask         |
| `RATE_LIMIT_PER_MINUTE` | `120`                                  | Applied to search and recommendation endpoints |

Frontend variables live in `frontend/.env.example`; both are optional in development.

Never commit a real `.env` — it is in `.gitignore`.

---

## Running the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- API root: <http://localhost:8000/api>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health: <http://localhost:8000/api/health>

### Admin API

Destructive endpoints are disabled until you set `ADMIN_API_KEY`, and then require the
`X-Admin-Api-Key` header.

```bash
curl -X POST http://localhost:8000/api/admin/tools \
  -H "X-Admin-Api-Key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Example","website_url":"https://example.com","pricing_status":"FREE_TIER"}'
```

Available: create, update (PATCH), delete and deactivate tools; manage pricing plans, free-access
grants, verification metadata, categories, tags and collections.

---

## Running the frontend

```bash
cd frontend
npm run dev      # dev server on :5173 with API proxy
npm run build    # typecheck + production bundle into dist/
npm run preview  # serve the built bundle
npm run lint     # tsc --noEmit
```

---

## Seeding the database

```bash
cd backend
python -m app.seed            # insert or update
python -m app.seed --reset    # drop and rebuild (SQLite/dev only)
```

The seeder is idempotent and keyed on slugs, so re-running it updates existing records instead of
duplicating them. The dataset lives in `backend/app/seed/data/`:

```text
categories.json
collections.json
tools/01_development.json          # coding, agents, IDEs, review, testing, docs, DevOps, security
tools/02_generative.json           # image, video, audio, voice, music, design, presentations
tools/03_ai_engineering.json       # LLM runtimes, APIs, RAG, vector DBs, MCP, agent frameworks
tools/04_research_productivity.json # research, search, notes, meetings, learning
```

Adding a tool means adding one JSON object and re-running the seeder — no code changes.

---

## Running tests

```bash
cd backend
python -m pytest              # 80 tests
python -m pytest -v
python scripts/smoke.py       # hits every endpoint of a running server
```

Tests build a temporary SQLite database, seed it once per session and exercise the real API through
`httpx.AsyncClient`. They cover tool listing and pagination, tool detail, alternatives, pricing,
verification, 404 handling, search ranking and free-intent detection, category filtering, the free
tools page, recommendations (including that a nonsense query returns no best match), comparison
alignment, admin authentication and CRUD, plus unit tests for slugs, pricing wording, free-access
rendering, quality scoring, intent extraction and the integrity of the seed dataset itself.

---

## API documentation

FastAPI generates OpenAPI automatically at `/docs`, `/redoc` and `/openapi.json`.

| Method | Endpoint                          | Purpose                                     |
| ------ | --------------------------------- | ------------------------------------------- |
| GET    | `/api/home`                       | Everything the homepage renders             |
| GET    | `/api/tools`                      | Browse with filters, sorting and pagination |
| GET    | `/api/tools/{slug}`               | Full tool detail                            |
| POST   | `/api/tools/resolve`              | Hydrate a client-side list of slugs         |
| GET    | `/api/tools/{id}/alternatives`    | Similar tools                               |
| GET    | `/api/tools/{id}/pricing`         | Structured pricing plans                    |
| GET    | `/api/tools/{id}/verification`    | Verification metadata                       |
| GET    | `/api/categories`                 | Categories with tool and free-tool counts   |
| GET    | `/api/categories/{slug}/tools`    | Tools in a category                         |
| GET    | `/api/search?q=`                  | Search with facets and query interpretation |
| GET    | `/api/filters`                    | Every facet with live counts                |
| GET    | `/api/free-tools`                 | Free tools grouped by how they are free     |
| POST   | `/api/recommendations`            | Rule-based recommendations                  |
| POST   | `/api/recommendations/ai`         | LLM-assisted; falls back to rules           |
| POST   | `/api/recommendations/stack`      | Personal AI developer stack                 |
| POST   | `/api/compare`                    | Side-by-side comparison (2–4 tools)         |
| GET    | `/api/collections`                | Curated collections                         |
| GET    | `/api/collections/{slug}`         | Collection with its tools                   |
| GET/PUT/DELETE | `/api/favorites`          | Optional server-side favourites             |
| \*     | `/api/admin/*`                    | Authenticated content management            |

Collections respond with `{ "data": [...], "pagination": {...} }`, single resources with
`{ "data": {...} }`, and every error with:

```json
{ "error": { "code": "TOOL_NOT_FOUND", "message": "The requested tool could not be found." } }
```

### Recommendation scoring

```python
score = (
    category_match   * 30
    + keyword_match  * 25
    + technology_match * 20
    + feature_match  * 15
    + pricing_match  * 10
)
```

Only the dimensions your request actually expresses count toward the percentage, so a query with no
technology in it is not penalised for it. A tool that matches nothing you asked for is never
returned — being free is not on its own a reason to recommend something. Every response includes
the matched signals and the weights used.

---

## Data honesty rules

These are enforced in the seeder, the tests and the presentation layer:

1. A price is only stored when it can be traced to the provider's own pricing page, together with
   `last_verified_at` and `verification_source_url`. Otherwise the UI says
   "Pricing information unavailable. Check the provider's official pricing page."
2. Free-access limits are never invented. When the exact allowance is unknown, the record carries a
   qualitative description instead of a number.
3. `FREE_TRIAL` is never rendered as "free". Restrictions (watermarks, credit card, expiry) are
   shown next to the benefit, not hidden below it.
4. Comparison cells distinguish "no" from "we do not know" — a blank cell means unverified.
5. Records older than 180 days are flagged as stale in the UI.

---

## Future roadmap

The code is structured so these can be added without a rewrite:

- **Semantic search** with `pgvector` — the search repository already isolates the ranking
  expression per dialect
- **LLM re-ranking** — `POST /api/recommendations/ai` and `app/services/llm/` define the provider
  interface; the MVP never requires an API key
- **Automated tool discovery** — `app/services/discovery/` sketches the
  scheduler → research agent → web search → metadata extraction → pricing verification → quality
  scoring → admin approval pipeline. Nothing is published unverified.
- **Pricing change detection** — pricing is already structured per plan, so a diff produces a
  change record rather than an overwrite
- **User accounts** — `Favorite` is keyed by an anonymous client id today; adding a `user_id`
  column is the whole migration
- **Community** — reviews, submissions and voting, once there are accounts to attach them to
