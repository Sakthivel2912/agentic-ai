# AI Council Project Audit

**Date:** 2026-09-19

**Scope:** Existing backend, frontend, database, authentication, agents, workflow, RAG, SSE, Docker, configuration, and tests.

## Decision

The application database is SQLite. MongoDB is not part of the project architecture or runtime. The backend uses SQLite with SQLAlchemy and `aiosqlite`, and Docker persists the SQLite database through a volume.

## Current Status

| Area | Status | Notes |
| --- | --- | --- |
| Frontend TypeScript | WORKING | `npm run type-check` passes. |
| Frontend production build | WORKING | `npm run build` passes. |
| Frontend routing | PARTIALLY WORKING | Public and protected routes exist; several screens are placeholders. |
| Backend compilation | BROKEN | Four endpoint modules previously contained indentation errors. |
| Backend startup | BROKEN | Must be verified after endpoint repair and dependency checks. |
| SQLite persistence | PARTIALLY WORKING | Models and services exist; session lifecycle usage is inconsistent. |
| Authentication | PARTIALLY WORKING | JWT and password hashing exist, but API behavior depends on backend repair. |
| Research CRUD | PARTIALLY WORKING | Route and service code exist but require runtime validation. |
| Research answer workflow | PLACEHOLDER/PARTIAL | Workflow exists, but the start path does not reliably execute and persist a final answer. |
| Pinecone/RAG | MISSING | No complete ingestion, embedding, indexing, or retrieval pipeline. |
| External research discovery | MISSING | No provider implementation exists. |
| SSE | PARTIALLY WORKING | Service and frontend hook exist; authentication and real workflow events are incomplete. |
| Documents/Reports/Evaluations UI | PLACEHOLDER | Screens are not connected to their APIs. |

## Existing Architecture

```text
React + TypeScript + Vite
        |
        v
FastAPI REST API + SSE
        |
        v
SQLite + SQLAlchemy
        |
        v
Research services and LangGraph workflow
        |
        +--> Specialist agents
        +--> Reviewer
        +--> Synthesizer
        +--> Groq / LangChain
```

## Existing Project Areas

### Frontend

- `frontend/src/App.tsx`: route configuration.
- `frontend/src/api/`: Axios client, auth API, and research API.
- `frontend/src/store/`: persisted auth and research Zustand stores.
- `frontend/src/hooks/`: auth and SSE hooks.
- `frontend/src/pages/`: login, registration, dashboard, research creation, history, details, and additional placeholder screens.
- `frontend/src/components/`: layout, protected route, and reusable button.
- `frontend/src/index.css`: colorful teal, mint, and coral theme.

### Backend

- `backend/app/main.py`: FastAPI application and lifespan.
- `backend/app/database/sqlite.py`: SQLAlchemy engines and SQLite session factory.
- `backend/app/models/`: SQLAlchemy models and enums.
- `backend/app/schemas/`: Pydantic request and response schemas.
- `backend/app/services/`: authentication, research, agents, documents, reports, evaluations, and SSE services.
- `backend/app/api/v1/endpoints/`: auth, research, documents, reports, evaluations, and events routes.
- `backend/app/agents/`: six specialist agents, reviewer, and synthesizer.
- `backend/app/workflows/research_workflow.py`: LangGraph state and conditional agent routing.
- `backend/app/llm/groq_client.py`: LangChain Groq client.

## Existing API Routes

All routes are mounted under `/api/v1`.

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/login/form`
- `GET /auth/me`
- `PATCH /auth/me`
- `POST /auth/change-password`
- `POST /auth/logout`

### Research

- `POST /research/sessions`
- `GET /research/sessions`
- `GET /research/sessions/{session_id}`
- `PUT /research/sessions/{session_id}`
- `DELETE /research/sessions/{session_id}`
- `POST /research/sessions/{session_id}/start`
- `POST /research/sessions/{session_id}/cancel`

### Other Routes

- `GET /events/sessions/{session_id}/stream`
- Document upload, list, get, update, delete, and reindex routes.
- Report creation, generation, list, and get routes.
- Evaluation creation, run, list, and get routes.
- `GET /health`
- `GET /`
- `/api/docs`
- `/api/redoc`

These are source-defined routes and must be runtime-tested after backend repair.

## Authentication Review

### Present

- JWT creation and decoding.
- Bcrypt password hashing.
- Pydantic validation for registration and login.
- Bearer token injection in Axios requests.
- Zustand auth persistence.
- Protected frontend routes.
- HTTP 401 logout and redirect behavior.
- Ownership checks are attempted in service methods.

### Problems

- Some routes call the async SQLite session generator as though it directly returned an `AsyncSession`.
- Login, registration, and protected API calls cannot be accepted as working until the backend starts and a request test passes.
- The SSE endpoint does not currently authenticate the stream.

## Research and Agent Review

### Existing Agents

- Research
- Technical
- Cost and infrastructure
- Data analysis
- Product and business
- Security and risk
- Critical reviewer
- Master synthesizer

### Existing Workflow

The LangGraph workflow starts with the research agent and conditionally routes through selected technical, cost, data, product, and security agents. It can then run the reviewer and synthesizer.

### Missing or Incomplete

- Research start does not reliably launch a tracked background workflow.
- Agent execution persistence is incomplete and the execution service contains stub output behavior.
- No cancellation or retry orchestration.
- No reliable final report persistence.
- No real external paper discovery.
- No private document retrieval branch.
- No complete source attribution.
- No verified workflow event stream.

## RAG and Pinecone

Status: **MISSING**.

The repository contains dependency entries and an empty RAG package, but no complete implementation for:

- PDF, TXT, or DOCX extraction.
- Text chunking.
- Sentence-transformer embeddings.
- Pinecone client/index management.
- User-filtered retrieval.
- Chunk metadata.
- Reindexing and retry processing.
- Source attribution in final answers.

The intended future flow is:

```text
Upload
  -> extract text
  -> split chunks
  -> embed
  -> index in Pinecone
  -> store status in SQLite
  -> retrieve user-owned context
  -> pass evidence to agents
```

## External Research Discovery

Status: **MISSING**.

There is no research-provider package for OpenAlex, Semantic Scholar, arXiv, or PubMed. Provider normalization, deduplication, relevance ranking, caching, paper persistence, and paper UI are not implemented.

## Docker and Environment

### Docker

`docker-compose.yml` contains backend and frontend services. The backend uses `SQLITE_DATABASE=/data/ai_council.db` and persists `/data` through the `sqlite_data` volume. There is no database service container.

### Environment

The root `.env` is loaded by the backend. The frontend uses `frontend/.env` and `VITE_API_URL`.

SQLite-related configuration:

```env
SQLITE_DATABASE=ai_council.db
```

Groq and Pinecone variables remain because they are external AI/vector services, not application databases.

Never place server API keys in `VITE_*` variables or commit `.env`.

## Security Findings

### Present

- Password hashing.
- JWT helpers.
- Input validation.
- CORS configuration.
- File extension and upload-size checks.
- Intended ownership checks.

### Required Fixes

- Rotate any credentials that were exposed in the local environment.
- Authenticate and authorize SSE streams.
- Verify safe upload filenames and path traversal protection.
- Avoid logging secrets.
- Add request, session, user, and agent correlation fields to logs.
- Test every ownership check against a second user.

## Broken and Placeholder Code

### Backend

- Indentation errors were identified in `research.py`, `documents.py`, `reports.py`, and `evaluations.py`.
- SQLite session lifecycle is inconsistent.
- Research start behavior stops at status update.
- Agent execution service contains placeholder output behavior.
- No backend test modules exist beyond the tests package initializer.

### Frontend

- Documents, reports, and evaluations screens are static placeholders.
- Dashboard statistics and recent research are hardcoded examples.
- Knowledge, agent monitor, settings, and profile require API-backed review.
- No frontend unit or browser test suite exists.

## Recommended Implementation Order

1. Repair backend endpoint indentation and imports.
2. Standardize the SQLite session lifecycle.
3. Add health, auth, and research CRUD tests.
4. Connect research start to a tracked background workflow.
5. Persist agent execution, reviewer, synthesizer, final answer, and errors.
6. Emit authenticated real SSE events.
7. Implement document extraction, chunking, embeddings, Pinecone indexing, and retrieval.
8. Implement external research providers and paper persistence.
9. Connect Documents, Reports, Evaluations, Knowledge, Agent Monitor, and Dashboard to real APIs.
10. Add retry, cancellation, exports, loading states, error states, and end-to-end tests.

## Files to Modify First

- `backend/app/api/v1/endpoints/auth.py`
- `backend/app/api/v1/endpoints/research.py`
- `backend/app/api/v1/endpoints/documents.py`
- `backend/app/api/v1/endpoints/reports.py`
- `backend/app/api/v1/endpoints/evaluations.py`
- `backend/app/api/dependencies.py`
- `backend/app/database/sqlite.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/research_service.py`
- `backend/app/services/agent_execution_service.py`
- `backend/app/workflows/research_workflow.py`
- `docker-compose.yml`

## Files to Preserve Initially

- Existing frontend route structure.
- `frontend/src/api/client.ts`.
- Auth and research Zustand stores.
- Existing specialist agent names and workflow shape.
- JWT and password utility functions, after request tests pass.

## Files to Remove Only After Verification

- Any obsolete non-SQLite database module or import.
- Unused database dependencies after confirming the active requirements.
- Placeholder agent output paths after real execution is persisted.
- Historical documentation that contradicts SQLite.

## Acceptance Gate

Do not call the project complete until this flow passes:

```text
Register
  -> Login
  -> SQLite user
  -> Create research session
  -> Start session
  -> Tracked workflow
  -> Specialist agents
  -> Reviewer
  -> Synthesizer
  -> SQLite final answer/report
  -> Authenticated SSE events
  -> Completed research shown in React
```

Audit complete. The next implementation phase is backend startup repair and SQLite session stabilization.
