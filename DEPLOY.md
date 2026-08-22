# Deploy DevAI Hub

This project is **two services**:

| Piece | Host | Why |
|-------|------|-----|
| React frontend (`frontend/`) | **Vercel** | Static Vite build |
| FastAPI backend (`backend/`) | **Render** (free) | Vercel cannot run this FastAPI + SQLite app as-is |

---

## 1. Deploy the API on Render (do this first)

1. Open [https://dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
2. **New** → **Blueprint** → select `Ahsan1974/Dev-AI-Hub`.
3. Render reads `render.yaml` and creates `devai-hub-api`.
4. Wait for the first deploy (auto-seed loads ~500 tools; first boot can take a few minutes).
5. Copy the service URL, e.g. `https://devai-hub-api.onrender.com`.
6. Confirm health: `https://YOUR-API.onrender.com/api/health`

> Free Render apps sleep after idle time. The first request after sleep can take ~30–60s.

---

## 2. Deploy the frontend on Vercel

1. Open [https://vercel.com/new](https://vercel.com/new).
2. Import **`Ahsan1974/Dev-AI-Hub`**.
3. Configure:
   - **Framework Preset:** Vite  
   - **Root Directory:** `frontend`  
   - **Build Command:** `npm run build`  
   - **Output Directory:** `dist`
4. **Environment Variables** → add:

   | Name | Value |
   |------|-------|
   | `VITE_API_BASE_URL` | `https://YOUR-API.onrender.com/api` |

5. Deploy.
6. Copy your Vercel URL (e.g. `https://dev-ai-hub.vercel.app`).

---

## 3. Wire CORS

On Render → `devai-hub-api` → **Environment** → set:

```text
CORS_ORIGINS=https://YOUR-VERCEL-URL.vercel.app,http://localhost:5173
```

Redeploy the API (or wait for auto-redeploy).  
`*.vercel.app` preview URLs are already allowed via regex in the API.

---

## Local development (unchanged)

```powershell
.\start.ps1
```

- App: http://localhost:5173  
- API docs: http://localhost:8000/docs  

---

## Environment cheat sheet

### Frontend (Vercel)

```env
VITE_API_BASE_URL=https://YOUR-API.onrender.com/api
```

### Backend (Render)

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///./devai_hub.db
AUTO_SEED=true
CORS_ORIGINS=https://YOUR-VERCEL-URL.vercel.app
```
