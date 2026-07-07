# Deployment Guide — AI UPSC Study OS

**Stack:** Vercel (frontend) + Railway (backend) + Neon (database) — **$0/month**

---

## Prerequisites

- GitHub account
- [Neon](https://neon.tech) — database (connected)
- [Railway](https://railway.com) — backend
- [Vercel](https://vercel.com) — frontend

---

## Step 1 — Push to GitHub

```powershell
cd f:\Developer
git init
git add .
git commit -m "AI UPSC Study OS — production ready"
git remote add origin https://github.com/YOUR_USERNAME/upsc-study-os.git
git push -u origin main
```

Never commit `backend/.env` (already in `.gitignore`).

---

## Step 2 — Neon database

1. Neon Console → your project → **Connection details**
2. Copy **Pooled connection** string
3. Ensure it ends with `?sslmode=require`

Local / Railway variable:

```env
DATABASE_URL=postgresql://...@ep-xxx-pooler....neon.tech/neondb?sslmode=require
```

**Initialize schema** (once):

```powershell
cd backend
python -m alembic upgrade head
python scripts/seed_data.py
```

---

## Step 3 — Deploy backend (Railway)

### Create service

1. https://railway.com → **New Project** → **Deploy from GitHub**
2. Connect your `digvi08/upsc-study-os` repo
3. Set the service root to `backend`
4. Railway will detect the `Dockerfile` and build the backend automatically
5. Optional: set the health check path to `/health`

### Environment variables

Copy from `backend/.env.production.example`:

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Neon pooled connection string |
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `ALLOWED_ORIGINS` | `https://YOUR-APP.vercel.app` *(set after Step 4)* |
| `FRONTEND_URL` | `https://YOUR-APP.vercel.app` |
| `AI_PROVIDER` | Optional (`auto`, `openai`, or `gemmini`) |
| `OPENAI_API_KEY` | Optional |
| `GEMMINI_API_BASE_URL` | Optional — your Gemmini-compatible API base URL, e.g. `https://your-gemmini-host/v1` |
| `GEMMINI_API_KEY` | Optional — your Gemmini service auth key if required |
| `GOOGLE_CLIENT_ID` | Optional |
| `GOOGLE_CLIENT_SECRET` | Optional |

Railway deploys the backend using `backend/Dockerfile`.

**Seed production data** (Railway shell, once):

```bash
python scripts/seed_data.py
```

Test: `https://YOUR-API.onrailway.app/health`

---

## Step 4 — Deploy frontend (Vercel)

1. https://vercel.com → **Add New Project** → import repo
2. Settings:

| Field | Value |
|-------|--------|
| Root Directory | `frontend` |
| Framework | Angular |
| Build Command | `npm run build:prod` |
| Output Directory | `dist/upsc-study-os` |
| Install Command | `npm install --legacy-peer-deps` |

3. **Environment Variables** (Vercel → Settings → Environment Variables):

| Name | Value | Environments |
|------|--------|--------------|
| `NG_APP_API_URL` | `https://YOUR-API.onrailway.app/api/v1` | Production |
| `NG_APP_GOOGLE_CLIENT_ID` | Your Google client ID *(optional)* | Production |

The build runs `scripts/inject-env.mjs` which writes `environment.prod.ts` automatically. In production, `NG_APP_API_URL` is required and the build will now fail if it is missing.

4. Deploy → copy URL: `https://your-app.vercel.app`

---

## Step 5 — Link frontend ↔ backend

1. **Railway** → update:
   ```env
   ALLOWED_ORIGINS=https://your-app.vercel.app
   FRONTEND_URL=https://your-app.vercel.app
   ```
2. **Manual Deploy** on Railway
3. Open Vercel URL → Register → test PYQ / AI Mentor

---

## Step 6 — Google OAuth (optional)

Google Cloud Console → OAuth client:

**Authorized JavaScript origins:**
```
https://your-app.vercel.app
```

**Authorized redirect URIs:**
```
https://your-app.vercel.app/auth/google/callback
```

Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` on Railway and `NG_APP_GOOGLE_CLIENT_ID` on Vercel.

---

## Local development (Neon)

```powershell
cd backend
copy .env.example .env
# Edit DATABASE_URL with Neon string
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

```powershell
cd frontend
copy src\environments\environment.example.ts src\environments\environment.ts
npm install --legacy-peer-deps
npm start
```

---

## Production checklist

- [ ] `SECRET_KEY` is random 32+ chars on Railway
- [ ] `DEBUG=false`, `ENVIRONMENT=production`
- [ ] `ALLOWED_ORIGINS` = exact Vercel URL (no trailing slash)
- [ ] `NG_APP_API_URL` set on Vercel
- [ ] Alembic migrations ran (automatic via `start.sh`)
- [ ] `python scripts/seed_data.py` run once on production
- [ ] Rotate Neon password if it was ever exposed

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS error | Match `ALLOWED_ORIGINS` to Vercel URL exactly |
| 502 / slow API | Railway free tier cold start — wait 60s |
| App shows localhost API | Set `NG_APP_API_URL` on Vercel, redeploy |
| `SECRET_KEY` startup error | Use 32+ char random secret in production |
| Empty PYQs | Run `seed_data.py` on Railway shell |

---

## Architecture

```
Browser → Vercel (Angular)
              ↓ HTTPS
         Railway (FastAPI + Docker)
              ↓ SSL
         Neon (PostgreSQL pooled)
```
