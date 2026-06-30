---
name: UPSC Study OS Project Context
description: "Use when: working on any file in this UPSC Study OS project. Provides global context about project architecture, conventions, and best practices."
applyTo: ["**/*.ts", "**/*.py", "**/*.json", "frontend/**", "backend/**"]
---

# UPSC Study OS Project Context

This is a comprehensive AI-powered UPSC/MPSC Study Operating System with production-ready infrastructure.

## Quick Reference

### Project Stack
- **Frontend**: Angular 19, Tailwind CSS, Angular Material, RxJS
- **Backend**: FastAPI, SQLAlchemy ORM, Pydantic
- **Database**: PostgreSQL
- **AI**: OpenAI API, Embeddings, Vector Search
- **Auth**: JWT + Google OAuth
- **OCR**: Tesseract OCR
- **Storage**: Cloudinary / AWS S3
- **Deployment**: Vercel (FE), Render (BE), Neon (DB)

### Directory Structure
- `frontend/` - Angular 19 application
- `backend/` - FastAPI application
- `.github/agents/` - Custom agents
- `.github/instructions/` - Development instructions

### Environment Variables
- **Backend**: `backend/.env.example`
- **Frontend**: `frontend/src/environments/environment.example.ts`

## Key Development Patterns

### Backend (FastAPI)
1. **Models**: `backend/app/models/` - SQLAlchemy ORM models
2. **Schemas**: `backend/app/schemas/` - Pydantic validation schemas
3. **Routes**: `backend/app/api/routes/` - FastAPI endpoints
4. **Services**: `backend/app/services/` - Business logic
5. **Migrations**: `backend/migrations/` - Alembic database migrations

### Frontend (Angular)
1. **Modules**: `frontend/src/app/modules/` - Feature modules
2. **Services**: `frontend/src/app/core/services/` - API and utility services
3. **Components**: Generate with `ng generate component`
4. **Routing**: `frontend/src/app/app-routing.module.ts`
5. **Styling**: Tailwind CSS + Angular Material

## Standards & Conventions

### Python (Backend)
- Use type hints: `def get_user(user_id: int) -> User:`
- Follow PEP 8 style
- Add docstrings to functions
- Use SQLAlchemy relationships properly
- Validate with Pydantic schemas

### TypeScript (Frontend)
- Use strict mode
- Add type annotations
- Use RxJS Observables for async operations
- Follow Angular style guide
- Implement proper error handling

### Database
- Always use migrations for schema changes
- Create proper indexes for performance
- Use foreign keys for relationships
- Document complex queries

## Common Tasks

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp src/environments/environment.example.ts src/environments/environment.ts
ng serve
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Testing
```bash
cd backend
pytest tests/ -v
```

## Module Organization

### Core Modules
1. **Authentication** - User registration, login, JWT
2. **Dashboard** - User profile and overview
3. **Subjects** - Subject and topic hierarchy

### Feature Modules
4. **PYQ Analyzer** - Previous Year Questions
5. **AI Mentor** - GPT-powered tutoring
6. **Smart Notes** - Note management
7. **Revision** - Spaced repetition system
8. **Planner** - Daily study schedule
9. **Current Affairs** - News and topic linking
10. **Evaluation** - Answer grading
11. **Analytics** - Performance tracking
12. **Admin** - System administration

## Code Quality Checklist

- [ ] Code follows project conventions
- [ ] Type hints are present (Python/TypeScript)
- [ ] Error handling is comprehensive
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No hardcoded values (use env vars)
- [ ] Security best practices followed
- [ ] Performance is acceptable
- [ ] No console warnings or errors

## Important Notes

1. **Demo Mode AI**: If `OPENAI_API_KEY` not set, AI endpoints return demo responses
2. **Database**: Defaults to SQLite locally if `DATABASE_URL` not set
3. **CORS**: Configure allowed origins for each deployment environment
4. **Tests**: Run tests before committing: `pytest tests/ -v`
5. **Migration Safety**: Always backup database before running migrations
6. **API Docs**: Available at `http://localhost:8000/docs` when backend running

## Getting Help

- Check README.md for quick start
- Review DEPLOYMENT.md for production setup
- Check existing modules for code examples
- Use grep to find similar implementations
- Run tests to validate changes
