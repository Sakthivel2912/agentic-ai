# AI Council - Setup Guide

This guide provides step-by-step instructions for setting up and running the AI Council multi-agent research system.

## Prerequisites

### Required Software

- **Python 3.10+** (Python 3.11+ recommended)
- **Node.js 18+**
- **MongoDB 4.4+** (local installation or MongoDB Atlas account)
- **Git** (for cloning the repository)

### Required API Keys

- **Groq API Key** - For LLM inference
  - Get your key at: https://console.groq.com/
  - The project uses the `llama3-70b-8192` model by default

- **Pinecone API Key** (for RAG features - optional for basic functionality)
  - Get your key at: https://www.pinecone.io/
  - Required for document processing and retrieval

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-council
```

### 2. Environment Configuration

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_council

# Security
SECRET_KEY=your-secret-key-change-in-production-2024

# Groq API
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama3-70b-8192
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=4096

# Pinecone (for RAG features)
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX_NAME=ai-council
PINECONE_DIMENSION=384

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Frontend
VITE_API_URL=http://localhost:8000
```

**Important:** Never commit the `.env` file to version control. It contains sensitive API keys.

### 3. Start MongoDB

#### Option A: Local MongoDB Installation

**Windows:**
1. Download MongoDB from: https://www.mongodb.com/try/download/community
2. Install MongoDB Community Server
3. Start MongoDB service or run: `mongod`

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

#### Option B: Docker

```bash
docker-compose up -d mongodb
```

#### Option C: MongoDB Atlas (Cloud)

1. Create a free account at: https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get your connection string
4. Update `.env` with:
   ```
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
   ```

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Frontend: http://localhost:5173 (port may vary if 5173 is in use)

### Production Mode with Docker

```bash
docker-compose up -d
```

This will start:
- MongoDB
- Backend API
- Frontend (if configured in docker-compose.yml)

## Verification

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "AI Council",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. Check API Documentation

Open in browser: http://localhost:8000/api/docs

### 3. Test Authentication

1. Open frontend: http://localhost:5173
2. Click "Register"
3. Create an account
4. Log in with your credentials
5. You should see the dashboard

### 4. Test Research Session

1. Navigate to "Research History"
2. Click "New Research"
3. Fill in the form:
   - Title: "Test Research"
   - Question: "What are the benefits of microservices architecture?"
   - Select a few agents
4. Click "Create Session"
5. The session should appear in the history

## Troubleshooting

### MongoDB Connection Failed

**Error:** `pymongo.errors.ServerSelectionTimeoutError`

**Solutions:**
1. Ensure MongoDB is running: `mongod` or check Docker
2. Check MongoDB URI in `.env`
3. Verify MongoDB is accessible on the configured port (default 27017)
4. Check firewall settings

### Groq API Key Not Set

**Error:** `ValueError: GROQ_API_KEY is not set in environment variables`

**Solutions:**
1. Add your Groq API key to `.env`
2. Restart the backend server
3. Ensure `.env` is in the backend directory

### Frontend Cannot Connect to Backend

**Error:** Network errors or CORS errors

**Solutions:**
1. Ensure backend is running on port 8000
2. Check `VITE_API_URL` in `.env`
3. Verify CORS configuration in `backend/app/core/config.py`
4. Check that frontend port is in `CORS_ORIGINS`

### Port Already in Use

**Error:** `Port 5173 is in use, trying another one...`

**Solutions:**
1. Vite will automatically try the next available port (5174, 5175, etc.)
2. Update `VITE_API_URL` in `.env` if the port changes
3. Or stop the process using the port

### Dependencies Installation Failed

**Error:** Python or npm installation errors

**Solutions:**
1. Ensure you're using Python 3.10+
2. Try creating a fresh virtual environment
3. Clear npm cache: `npm cache clean --force`
4. Delete `node_modules` and `venv` and reinstall

## Development Workflow

### Making Backend Changes

1. Edit Python files in `backend/app/`
2. Uvicorn with `--reload` will automatically restart
3. Check console for errors
4. Verify changes in API docs: http://localhost:8000/api/docs

### Making Frontend Changes

1. Edit React/TypeScript files in `frontend/src/`
2. Vite with HMR will automatically reload
3. Check browser console for errors
4. Changes should appear immediately

### Database Schema Changes

1. Update models in `backend/app/models/`
2. Beanie will automatically create indexes on first use
3. For manual index creation, use MongoDB Compass or CLI

## API Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Create Research Session

```bash
curl -X POST http://localhost:8000/api/v1/research/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "title": "Microservices Analysis",
    "question": "What are the pros and cons of microservices?",
    "category": "software_architecture",
    "selected_agents": ["research_agent", "technical_agent"],
    "enable_rag": false,
    "enable_review": true
  }'
```

### Start Research Session

```bash
curl -X POST http://localhost:8000/api/v1/research/sessions/<session-id>/start \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Production Deployment

### Environment Variables

For production, update these in your production environment:

```env
SECRET_KEY=<strong-random-key>
MONGODB_URI=<production-mongodb-uri>
GROQ_API_KEY=<production-groq-key>
PINECONE_API_KEY=<production-pinecone-key>
```

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Security Considerations

1. **Never commit `.env`** to version control
2. Use strong, randomly generated SECRET_KEY
3. Use HTTPS in production
4. Enable rate limiting (slowapi is installed)
5. Keep dependencies updated
6. Use firewall rules to restrict database access
7. Enable MongoDB authentication

## Next Steps

After successful setup:

1. Create a test user account
2. Create a research session
3. Test the multi-agent workflow (requires Groq API key)
4. Upload documents (requires MongoDB and Pinecone)
5. Generate reports
6. Run evaluations

## Support

For additional help:

1. Check the phase completion docs in `docs/`
2. Review the API documentation at `/api/docs`
3. Check the logs in the terminal
4. Review error messages in browser console
