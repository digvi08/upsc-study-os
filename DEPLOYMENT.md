# Deployment Guide — AI UPSC Study OS

**Stack:** Vercel (frontend) + Render (backend) + Neon (database) — **$0/month**

---

## Prerequisites

- GitHub account
- [Neon](https://neon.tech) — database (connected)
- [Render](https://render.com) — backend
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

Local / Render variable:

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

## Step 3 — Deploy backend (Render)

### Create service

1. https://dashboard.render.com → **New +** → **Web Service**
2. Connect GitHub repo
3. Settings:

| Field | Value |
|-------|--------|
| Root Directory | `backend` |
| Runtime | **Docker** |
| Plan | **Free** |
| Health Check Path | `/health` |

Or use **Blueprint** with root `render.yaml`.

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
| `OPENAI_API_KEY` | Optional |
| `GOOGLE_CLIENT_ID` | Optional |
| `GOOGLE_CLIENT_SECRET` | Optional |

Deploy → note URL: `https://upsc-study-os-api.onrender.com`

`start.sh` runs `alembic upgrade head` on every deploy.

**Seed production data** (Render Shell, once):

```bash
python scripts/seed_data.py
```

Test: `https://YOUR-API.onrender.com/health`

---

## Step 4 — Deploy frontend (Vercel)

1. https://vercel.com → **Add New Project** → import repo
2. Settings:

| Field | Value |
|-------|--------|
| Root Directory | `frontend` |
| Framework | Angular |
| Build Command | `npm run build:prod` |
| Output Directory | `dist/upsc-study-os/browser` |
| Install Command | `npm install --legacy-peer-deps` |

3. **Environment Variables** (Vercel → Settings → Environment Variables):

| Name | Value | Environments |
|------|--------|--------------|
| `NG_APP_API_URL` | `https://YOUR-API.onrender.com/api/v1` | Production |
| `NG_APP_GOOGLE_CLIENT_ID` | Your Google client ID *(optional)* | Production |

The build runs `scripts/inject-env.mjs` which writes `environment.prod.ts` automatically.

4. Deploy → copy URL: `https://your-app.vercel.app`

---

## Step 5 — Link frontend ↔ backend

1. **Render** → update:
   ```env
   ALLOWED_ORIGINS=https://your-app.vercel.app
   FRONTEND_URL=https://your-app.vercel.app
   ```
2. **Manual Deploy** on Render
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

Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` on Render and `NG_APP_GOOGLE_CLIENT_ID` on Vercel.

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

- [ ] `SECRET_KEY` is random 32+ chars on Render
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
| 502 / slow API | Render free tier cold start — wait 60s |
| App shows localhost API | Set `NG_APP_API_URL` on Vercel, redeploy |
| `SECRET_KEY` startup error | Use 32+ char random secret in production |
| Empty PYQs | Run `seed_data.py` on Render shell |

---

## Architecture

```
Browser → Vercel (Angular)
              ↓ HTTPS
         Render (FastAPI + Docker)
              ↓ SSL
         Neon (PostgreSQL pooled)
```
