# AI UPSC Study OS

A production-ready AI-powered UPSC/MPSC Study Operating System — your personal AI mentor and preparation management platform.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Angular 19, Tailwind CSS, Angular Material, RxJS, Chart.js |
| Backend | FastAPI (Python), SQLAlchemy ORM, Pydantic |
| Database | PostgreSQL |
| Auth | JWT + Google OAuth |
| AI | OpenAI API, Embeddings, Vector Search |
| OCR | Tesseract OCR |
| Storage | Cloudinary / AWS S3 |
| Deployment | Vercel (FE), Render/Railway (BE), Supabase/Neon (DB) |

## Modules

1. Authentication System
2. User Dashboard
3. Subject & Topic Management
4. PYQ Analyzer
5. AI Mentor
6. Smart Notes
7. Revision System
8. Daily Planner
9. Current Affairs Linker
10. Answer Evaluation
11. Analytics Dashboard
12. Admin Panel

## Project Structure

```
upsc-study-os/
├── frontend/          # Angular 19 application
├── backend/           # FastAPI application
├── docker-compose.yml
└── README.md
```

## Quick Start
 
### Fastest way: Run the full stack with Docker
```bash
docker compose up --build
```
Open the app at `http://localhost` once the backend and frontend services are ready.

When you're done, stop the stack with:
```bash
docker compose down
```

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Shortcut scripts
If you are on Windows, run:
```powershell
.\run-dev.bat
```
On macOS/Linux, run:
```bash
./run-dev.sh
```
Then stop with:
```bash
docker compose down
```

### Local development (optional)
If you prefer running backend and frontend separately:

#### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env      # On Windows use: copy .env.example .env
# Update .env values as needed
alembic upgrade head
python -m uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp src/environments/environment.example.ts src/environments/environment.ts  # On Windows use: copy src\environments\environment.example.ts src\environments\environment.ts
npm start
```

## Environment Variables

See `backend/.env.example` and `frontend/src/environments/environment.example.ts`.

## Development Phases

- **Phase 1**: Auth, Dashboard, Subject/Topic Management, Notes CRUD ✅
- **Phase 2**: PYQ Analyzer ✅
- **Phase 3**: AI Mentor ✅
- **Phase 4**: Revision System ✅
- **Phase 5**: Daily Planner ✅
- **Phase 6**: Current Affairs Linker ✅
- **Phase 7**: Answer Evaluation ✅
- **Phase 8**: Analytics ✅

## Seed Sample Data

After starting PostgreSQL and running migrations:

```bash
cd backend
python scripts/seed_data.py
```

This loads sample PYQs (Monsoon, Federalism, Landforms) and current affairs for development.

## Running Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

## AI Features (Demo Mode)

If `OPENAI_API_KEY` is not set, the AI Mentor returns structured demo responses so you can test the UI without an API key. Set a valid key in `backend/.env` for full GPT-powered responses.

## API Documentation

Once backend is running, visit: `http://localhost:8000/docs`

## Free Deployment (Vercel + Render + Neon)

Production-ready config included (`render.yaml`, `vercel.json`, env injection).

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for the full deploy checklist.

**Quick env vars:**

| Platform | Key | Example |
|----------|-----|---------|
| Neon | `DATABASE_URL` | `postgresql://...@ep-xxx-pooler.neon.tech/neondb?sslmode=require` |
| Render | `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| Vercel | `NG_APP_API_URL` | `https://your-api.onrender.com/api/v1` |

## License

MIT
