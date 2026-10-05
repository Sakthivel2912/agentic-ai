# AI Council

AI Council is a multi-agent research and decision-support application. A user creates a research question, selects specialist agents, and receives a structured answer through a React interface backed by FastAPI and LLM services.

## Current Status

**Frontend:** Build-ready and visually refreshed.

**Backend:** The API and background research workflow are implemented, and the Python source compiles. Research sessions use Groq and web search through DDGS. Runtime still requires installing backend dependencies and configuring the root `.env`; RAG retrieval is not implemented yet.

This README describes the project as it exists now, not the intended future architecture.

## What Has Been Built

### Frontend Application

- React 18 with TypeScript and Vite
- React Router routes for public and protected screens
- Zustand stores for authentication and research sessions
- Axios API client with bearer-token injection
- Automatic logout and redirect on HTTP 401 responses
- Login and registration forms
- Protected application layout with sidebar navigation
- Dashboard with research summary cards and system status
- New research session form
- Research history with status filtering, pagination, viewing, and deletion
- Research details screen with status, progress, agent outputs, final answer, sources, and metadata
- SSE hook for progress, agent output, error, completion, and keepalive events
- Placeholder screens for documents, reports, evaluations, knowledge, settings, and profile
- Responsive colorful UI theme using teal, mint, coral, layered gradients, grid texture, glass panels, and animated page entry

### Backend Application

- FastAPI application entry point
- Pydantic settings and request/response schemas
- SQLite and SQLAlchemy database layer currently used by the implementation
- JWT creation and validation
- Bcrypt password hashing
- User registration, login, profile, password change, and logout route definitions
- Research session CRUD route definitions
- Document, report, evaluation, and SSE route definitions
- Service modules for authentication, research, agents, documents, reports, evaluations, and SSE
- Six specialist agent modules:
  - Research
  - Technical
  - Cost and infrastructure
  - Data analysis
  - Product and business
  - Security and risk
- Reviewer and synthesizer agent modules
- LangGraph workflow definition
- Groq client integration
- Dockerfiles and Docker Compose configuration
- Structured logging configuration

### Project Maintenance

- Removed obsolete audit and setup documents that contradicted the current source tree
- Removed generated Python cache directories outside virtual environments
- Added Vite environment typings
- Fixed the nested React Router layout to render pages through `<Outlet />`
- Fixed frontend TypeScript configuration and unused-code errors
- Updated `.env.example` to cover the variables used by the current environment
- Made backend settings resolve the root `.env` consistently

## Architecture

```text
Browser
  |
  v
React + TypeScript + Vite
  |
  | Axios REST calls and EventSource updates
  v
FastAPI
  |
  v
SQLite / SQLAlchemy        Current implementation
  |
  v
Research services and agent workflow
  |
  v
Groq / LangChain / LangGraph
```

Pinecone and a complete RAG pipeline appear in planned integration areas, but they are not active database functionality in the current source tree.

## Main Routes

### Frontend Routes

| Route | Purpose |
| --- | --- |
| `/login` | Sign in |
| `/register` | Create an account |
| `/dashboard` | Overview dashboard |
| `/research/new` | Create a research session |
| `/research` | Research history |
| `/research/:id` | Session details and answer view |
| `/agent-monitor` | Agent monitoring screen |
| `/knowledge` | Knowledge screen |
| `/documents` | Document screen placeholder |
| `/reports` | Reports screen placeholder |
| `/evaluations` | Evaluations screen placeholder |
| `/settings` | Settings screen |
| `/profile` | User profile |

### Backend API Route Definitions

All API routes use the `/api/v1` prefix.

#### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/login/form`
- `GET /auth/me`
- `PATCH /auth/me`
- `POST /auth/change-password`
- `POST /auth/logout`

#### Research Sessions

- `POST /research/sessions`
- `GET /research/sessions`
- `GET /research/sessions/{session_id}`
- `PUT /research/sessions/{session_id}`
- `DELETE /research/sessions/{session_id}`
- `POST /research/sessions/{session_id}/start`
- `POST /research/sessions/{session_id}/cancel`

#### Real-Time Updates

- `GET /events/sessions/{session_id}/stream`

#### Documents

- `POST /documents/upload`
- `GET /documents/`
- `GET /documents/{document_id}`
- `PUT /documents/{document_id}`
- `DELETE /documents/{document_id}`
- `POST /documents/{document_id}/reindex`

#### Reports and Evaluations

- Report creation, generation, listing, and retrieval routes
- Evaluation creation, execution, listing, and retrieval routes

#### System

- `GET /health`
- `GET /`
- API documentation at `/api/docs`
- ReDoc at `/api/redoc`

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- agents/          Specialist, reviewer, and synthesizer agents
|   |   |-- api/             FastAPI dependencies and versioned endpoints
|   |   |-- core/            Configuration, logging, and security
|   |   |-- database/         SQLite connection and SQLAlchemy base
|   |   |-- models/           SQLAlchemy models
|   |   |-- schemas/          Pydantic request and response models
|   |   |-- services/         Business logic
|   |   |-- workflows/        LangGraph research workflow
|   |   |-- llm/              Groq client
|   |   |-- main.py           FastAPI application
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- tests/
|-- frontend/
|   |-- src/
|   |   |-- api/              Axios API modules
|   |   |-- components/       Shared UI and layout components
|   |   |-- hooks/            Authentication and SSE hooks
|   |   |-- pages/            Application screens
|   |   |-- store/             Zustand stores
|   |   |-- types/             TypeScript domain types
|   |   |-- App.tsx            Route configuration
|   |   |-- index.css          Global theme and utilities
|   |   `-- main.tsx           React entry point
|   |-- package.json
|   |-- vite.config.ts
|   `-- tsconfig.json
|-- docs/                     Phase notes and project summaries
|-- uploads/                  Local upload storage
|-- docker-compose.yml
|-- .env.example
|-- .gitignore
`-- README.md
```

## Environment Configuration

The root `.env` is used by the backend. The frontend reads `frontend/.env` through Vite.

Copy the template before configuring local values:

```powershell
Copy-Item .env.example .env
```

Important variables include:

```env
SQLITE_DATABASE=ai_council.db
SECRET_KEY=replace-with-a-long-random-secret
GROQ_API_KEY=replace-with-your-groq-key
GROQ_MODEL=openai/gpt-oss-20b
PINECONE_API_KEY=replace-with-your-pinecone-key
VITE_API_URL=http://localhost:8001
```

Do not commit `.env` or place API keys in frontend source code. Any credentials that have been shared publicly or pasted into chat should be rotated.

## Local Development

### Frontend

```powershell
Set-Location frontend
npm install
npm run dev
```

The Vite development server normally starts at `http://localhost:5173` and may select another port if needed.

### Frontend Validation

```powershell
Set-Location frontend
npm run type-check
npm run build
```

The current frontend passes both commands.

### Backend

```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

The local frontend configuration points to port `8002`. The root `.env` must contain a valid `GROQ_API_KEY` for analysis generation.

### Docker

```powershell
docker-compose up --build
```

Docker Compose is configured for the SQLite application database and uses port `8000` for the backend.

## Verification Performed

- Frontend TypeScript check passed with `npm run type-check`.
- Frontend production bundle passed with `npm run build`.
- Login page was opened in the Vite development server and visually checked at desktop size.
- Frontend routes, stores, API modules, and SSE hook were reviewed.
- Environment variable names in `.env` were compared with `.env.example`.
- Backend Python source compilation passed with `python -m compileall -q backend/app`.
- Web search returned source links in a direct DDGS adapter smoke test.
- Full backend startup was not verified because FastAPI and the rest of the backend requirements are not installed in the current virtual environment.

## Known Limitations and Next Work

### Highest Priority

1. Install backend requirements and verify startup with a configured Groq API key.
2. Review database session lifecycle in the remaining API routes.
3. Implement document retrieval for the RAG option.
4. Authenticate the SSE stream instead of relying on an unauthenticated session URL.

### Product Completion

1. Connect Documents, Reports, and Evaluations pages to their APIs.
2. Implement document text extraction, chunking, embeddings, and retrieval.
3. Replace dashboard placeholder statistics with live API data.
4. Add frontend and backend tests for registration, login, research creation, workflow completion, and SSE updates.
5. Verify Docker Compose against the active SQLite implementation.
6. Add loading, empty, retry, and failure states across all screens.

## License

This project is intended for educational and portfolio demonstration purposes.
