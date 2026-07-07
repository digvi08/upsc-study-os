Deployment automation and required secrets

This file explains the GitHub Actions workflows added to this repository and lists the repository secrets and values you must add to enable automatic cloud deployment (Vercel frontend and backend migrations).

Files added:
- .github/workflows/deploy-frontend.yml  — Builds frontend and deploys to Vercel using secrets
- .github/workflows/deploy-backend.yml   — Installs backend, runs migrations against NEON_DATABASE_URL and contains a placeholder for Railway deploy

Required GitHub repository secrets (add these under Settings → Secrets → Actions):

Core secrets:
- NEON_DATABASE_URL: The full Postgres connection string for your Neon (or other) PostgreSQL instance. Example: postgresql://user:pass@host:port/db?sslmode=require
- VERCEL_TOKEN: Personal Vercel token with permissions to deploy (create a temporary token in Vercel)
- VERCEL_ORG_ID: Your Vercel organization ID (found in Vercel project settings)
- VERCEL_PROJECT_ID: Your Vercel project ID (found in Vercel project settings)
- NG_APP_API_URL: The frontend API base URL (e.g., https://your-api.onrailway.app/api/v1). This will be injected at build time.
- SECRET_KEY: Secret key used by FastAPI app (keep it long and random)

Optional secrets (enable features as needed):
- REDIS_URL: e.g. redis://:<password>@<host>:6379/0 (if using Redis service)
- OPENAI_API_KEY: If you want AI features enabled
- RAILWAY_TOKEN: If you want to enable automatic Railway deploys from GitHub Actions
- RAILWAY_PROJECT_ID / RAILWAY_SERVICE_ID: Railway identifiers (used if enabling Railway deploy step)
- CLOUDINARY_URL or AWS_* for storage (if used by your app)
- GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET: For Google OAuth login

How the workflows work:
- Frontend workflow: Checks out the repo, installs Node 20, builds frontend using "npm run build:prod" and deploys to Vercel using the amondnet/vercel-action. The Vercel action requires VERCEL_TOKEN, VERCEL_ORG_ID and VERCEL_PROJECT_ID to be set as repository secrets.

- Backend workflow: Checks out the repo, installs Python 3.11, installs backend requirements, writes DATABASE_URL into backend/.env (for alembic), and runs `alembic upgrade head` against the NEON_DATABASE_URL secret. A final optional placeholder indicates how to deploy to Railway (disabled by default).

Steps to enable automatic deployment:
1. Create a Vercel project (or use an existing one). In Vercel project settings find and copy the Org ID and Project ID.
2. Create a Neon (or other) PostgreSQL database and copy the connection string. Set it as NEON_DATABASE_URL.
3. Go to GitHub → Your repository → Settings → Secrets → Actions and add the secrets listed above.
4. Push to the main branch. The `deploy-frontend.yml` and `deploy-backend.yml` workflows will run on push to main. The frontend workflow will deploy to Vercel; the backend workflow will run DB migrations against your DB. If you want full backend auto-deploy (Railway), add RAILWAY_TOKEN, project IDs, and follow Railway's documentation to enable CLI deploy in the workflow (contact me and I can add this step once you enable Railway tokens).

Security and best practices:
- Use short-lived or scoped tokens where possible.
- Do NOT commit secrets to the repository — use GitHub Secrets.
- Revoke tokens after testing if they were temporary.

If you want, I can now:
- Add the Railway deploy step (requires RAILWAY_TOKEN and IDs).
- Attempt to create a Neon project and provision the DB automatically (requires Neon API token).
- Create a Vercel project and deploy on your behalf (requires VERCEL_TOKEN).

Next steps (please choose):
- I can add Railway automatic deploy steps now (you will need to add RAILWAY_TOKEN and IDs).
- Or, provide the Vercel/Railway/Neon tokens now and I can attempt to perform the deployment for you.

Which do you prefer?