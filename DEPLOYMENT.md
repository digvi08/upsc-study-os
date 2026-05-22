# Free Deployment Guide — AI UPSC Study OS

Deploy for **$0/month** using free tiers:

| Part | Service | Free tier |
|------|---------|-----------|
| Frontend | [Vercel](https://vercel.com) | Unlimited hobby projects |
| Backend | [Render](https://render.com) | 750 hrs/month (sleeps when idle) |
| Database | [Neon](https://neon.tech) | 512 MB PostgreSQL |

**Total cost:** $0 (no credit card on Neon/Vercel; Render may ask for card but free tier works)

---

## Overview

```
User → Vercel (Angular) → Render (FastAPI) → Neon (PostgreSQL)
```

---

## Part 1 — Database (Neon) ~5 min

1. Sign up at https://neon.tech
2. **New Project** → name: `upsc-study-os` → region: closest to you
3. Copy the **connection string** (looks like):
   ```
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
4. Save it — you'll use this as `DATABASE_URL` on Render.

> Neon URLs often end with `/neondb`. You can keep that database name or create `upsc_study_os` in the SQL editor.

---

## Part 2 — Backend (Render) ~10 min

### Option A — Deploy from GitHub (recommended)

1. Push your code to GitHub (if not already):
   ```powershell
   cd f:\Developer
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/upsc-study-os.git
   git push -u origin main
   ```

2. Go to https://dashboard.render.com → **New +** → **Blueprint**
3. Connect your repo — Render reads `render.yaml` at the project root
4. Or manually: **New Web Service** → connect repo → set:
   - **Root Directory:** `backend`
   - **Runtime:** Docker *(or Python)*
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:**
     ```bash
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

### Environment variables (Render → Environment)

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Neon connection string (paste from Part 1) |
| `SECRET_KEY` | Run: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DEBUG` | `false` |
| `ENVIRONMENT` | `production` |
| `ALLOWED_ORIGINS` | `https://YOUR-APP.vercel.app` *(update after Vercel deploy)* |
| `OPENAI_API_KEY` | Your OpenAI key *(optional — demo mode works without)* |
| `GOOGLE_CLIENT_ID` | Optional |
| `GOOGLE_CLIENT_SECRET` | Optional |

5. Deploy → copy your backend URL, e.g. `https://upsc-study-os-api.onrender.com`

6. **Seed data** (one time) — Render Shell or local with production `DATABASE_URL`:
   ```bash
   python scripts/seed_data.py
   ```

7. Test: `https://YOUR-BACKEND.onrender.com/health`

> **Note:** Free Render services **sleep after ~15 min** of no traffic. First request may take 30–60 seconds (cold start).

---

## Part 3 — Frontend (Vercel) ~5 min

1. Sign up at https://vercel.com → **Add New Project**
2. Import your GitHub repo
3. Settings:
   - **Framework Preset:** Angular
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build:prod`
   - **Output Directory:** `dist/upsc-study-os/browser`

4. **Environment Variables** (Vercel → Settings → Environment Variables):

   | Name | Value |
   |------|--------|
   | `NG_APP_API_URL` | `https://YOUR-BACKEND.onrender.com/api/v1` |

   Then update `frontend/src/environments/environment.prod.ts` to use your backend URL (see below).

5. Deploy → copy URL, e.g. `https://upsc-study-os.vercel.app`

6. **Update Render CORS** — go back to Render env vars:
   ```
   ALLOWED_ORIGINS=https://upsc-study-os.vercel.app
   ```
   Redeploy backend if needed.

---

## Part 4 — Production config checklist

### `frontend/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://YOUR-BACKEND.onrender.com/api/v1',
  googleClientId: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
  appName: 'AI UPSC Study OS',
};
```

Commit and push → Vercel auto-redeploys.

### Google OAuth (optional)

In Google Cloud Console → OAuth client → **Authorized redirect URIs:**
```
https://YOUR-APP.vercel.app/auth/google/callback
```

---

## Part 5 — Verify production

1. Open Vercel URL → Register a new account
2. Dashboard loads with stats
3. PYQ Analyzer → search `Monsoon` (after seed)
4. AI Mentor → sends a response (demo or OpenAI)

---

## Alternative free backends

| Service | Pros | Cons |
|---------|------|------|
| **Render** | Easy, Docker support | Cold starts |
| **Fly.io** | Fast, global | Free tier limits changed |
| **Railway** | Simple UI | Limited free credits |
| **Koyeb** | Free tier | Smaller community |

Database alternatives: **Supabase** (Postgres + auth), **ElephantSQL** (small free DB).

---

## Optional: Redis (not required for MVP)

Revision/planner work without Redis. If you add caching later, use **Upstash Redis** (free tier).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| CORS error | Set `ALLOWED_ORIGINS` on Render to exact Vercel URL (no trailing slash) |
| 502 / timeout on first load | Render cold start — wait 60s and retry |
| Database SSL error | Add `?sslmode=require` to Neon `DATABASE_URL` |
| API 401 | Register/login again; check `apiUrl` in `environment.prod.ts` |
| Migrations failed | Run `alembic upgrade head` in Render shell with `DATABASE_URL` set |

---

## Security before going public

- [ ] Change `SECRET_KEY` to a random 32+ char string
- [ ] Set `DEBUG=false` on Render
- [ ] Never commit `.env` or API keys to GitHub
- [ ] Add `.env` to `.gitignore` if missing

---

## Custom domain (optional, still free on Vercel)

Vercel → Project → Domains → add your domain.  
Update `ALLOWED_ORIGINS` on Render to include the new domain.
