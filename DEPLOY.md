# Deploy DevAI Hub (Vercel)

Both the React frontend and FastAPI API run on **Vercel**.

| Piece | Vercel project | URL |
|-------|----------------|-----|
| Frontend | `dev-ai-hub` | https://dev-ai-hub.vercel.app |
| API | `dev-ai-hub-api` | https://dev-ai-hub-api.vercel.app |

The API ships a pre-built SQLite catalogue (`backend/data/catalogue.db`) and copies it to `/tmp` on each cold start.

---

## Environment variables

### Frontend (`dev-ai-hub`)

| Name | Value |
|------|-------|
| `VITE_API_BASE_URL` | `https://dev-ai-hub-api.vercel.app/api` |

### API (`dev-ai-hub-api`)

| Name | Value |
|------|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `AUTO_SEED` | `false` |
| `CORS_ORIGINS` | `https://dev-ai-hub.vercel.app` |

`DATABASE_URL` defaults to `sqlite+aiosqlite:////tmp/devai_hub.db` when `VERCEL=1`.

---

## Redeploy from CLI

```powershell
# API
cd backend
npx --prefix ..\frontend vercel --prod --yes --scope ahsannadeem432002-gmailcoms-projects

# Frontend
cd ..\frontend
npx vercel --prod --yes --scope ahsannadeem432002-gmailcoms-projects
```

---

## Local development (unchanged)

```powershell
.\start.ps1
```

- App: http://localhost:5173  
- API docs: http://localhost:8000/docs  

Optional: Render blueprint (`render.yaml`) remains available if you prefer a always-on free API host instead of Vercel Functions.
