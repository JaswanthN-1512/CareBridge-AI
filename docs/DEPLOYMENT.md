# CareBridge AI — Production Deployment Guide

## 1. Architecture & Deployment Topology

CareBridge AI utilizes a modern, decoupled production architecture separating client-side presentation from backend AI document intelligence:

```
+-------------------------------------------------------------+
|                 Frontend: Vercel Edge CDN                   |
|   React + TypeScript + Vite + Tailwind CSS                  |
|   Static Assets / SPA Rewrites / Security Headers           |
+------------------------------+------------------------------+
                               |
                   HTTPS API Calls (/api/*)
                               |
+------------------------------v------------------------------+
|                 Backend: Render / Railway                   |
|   FastAPI + PyMuPDF + LangChain + In-Memory FAISS Index     |
|   Zero-Persistence Memory / Emergency Guardrails            |
+-------------------------------------------------------------+
```

---

## 2. Option A: Deploying Frontend to Vercel

The frontend is optimized for zero-configuration deployment on **Vercel**.

### Step 1: Connect Repository
1. Log in to [Vercel](https://vercel.com) and click **Add New > Project**.
2. Import your CareBridge AI Git repository.

### Step 2: Configure Project Settings
- **Project Name:** `carebridge-ai`
- **Framework Preset:** `Vite`
- **Root Directory:** Click `Edit` and select `frontend`.
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### Step 3: Environment Variables
Add the following environment variable in the Vercel dashboard:

| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://carebridge-ai-backend.onrender.com` | Base URL of your deployed backend service (omit trailing slash). |

### Step 4: Deploy
Click **Deploy**. Vercel will build and distribute your static SPA across global edge nodes. The bundled [`frontend/vercel.json`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/frontend/vercel.json) will automatically enforce SPA client-side routing rewrites and OWASP security headers.

---

## 3. Option B: Deploying Backend to Render

The backend is configured for 1-click deployment using Render's Infrastructure-as-Code Blueprint ([`render.yaml`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/render.yaml)).

### Method 1: Using Render Blueprint (Recommended)
1. Log in to [Render](https://render.com) and navigate to **Blueprints**.
2. Click **New Blueprint Instance** and select your repository.
3. Render will parse [`render.yaml`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/render.yaml) and automatically provision the web service.
4. Input your `OPENAI_API_KEY` (or leave empty to run in deterministic offline demo mode).
5. Click **Apply**.

### Method 2: Manual Web Service Setup
1. In Render, select **New > Web Service**.
2. Connect your Git repository.
3. Set the following build and run parameters:
   - **Name:** `carebridge-ai-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/api/health`
4. Configure Environment Variables:

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Enables production log formatting |
| `LLM_PROVIDER` | `openai` *(or `mock`)* | Set to `mock` for 0-cost evaluation |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API secret |
| `EMBEDDING_PROVIDER` | `openai` *(or `mock`)* | Embedding provider |
| `VECTOR_STORE_TYPE` | `faiss` | High-efficiency in-memory FAISS |
| `FRONTEND_URL` | `https://carebridge-ai.vercel.app` | Comma-separated CORS allowed domains |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload size threshold |

5. Click **Create Web Service**.

---

## 4. Option C: Deploying Backend to Railway

1. Log in to [Railway](https://railway.app) and select **New Project > Deploy from GitHub repo**.
2. In **Settings**, set **Root Directory** to `/backend`.
3. Railway automatically detects [`backend/Procfile`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/Procfile) and [`backend/requirements.txt`](file:///c:/Users/jaswa/Desktop/CareBridge-AI/backend/requirements.txt).
4. In the **Variables** tab, add:
   - `ENVIRONMENT=production`
   - `LLM_PROVIDER=openai` (or `mock`)
   - `OPENAI_API_KEY=your_key_here`
   - `FRONTEND_URL=https://your-frontend-domain.vercel.app`
5. In **Networking**, click **Generate Domain** to receive your public HTTPS backend URL.

---

## 5. Post-Deployment Verification Checklist

Once deployed, execute this 5-point verification checklist:

1. **Health Telemetry:** Visit `https://your-backend.onrender.com/api/health`. Ensure response is `{"status": "healthy"}` and HTTP code is `200`.
2. **CORS Validation:** Open your frontend on Vercel, open browser Developer Tools (Network tab), and verify that requests to `/api/samples` return `200 OK` with valid `Access-Control-Allow-Origin` headers.
3. **Synthetic Benchmark Ingestion:** Click **Load Sample** (e.g. *Normal Metabolic Panel*) on the upload card. Ensure the processing stepper transitions cleanly and displays the 4 intelligence dashboard cards.
4. **Grounded RAG Chat:** Ask a question in the chat console (e.g., *"What was my fasting blood glucose?"*). Verify the answer cites Page 1 and displays the grounding badge.
5. **Emergency Interception:** Type `"I have severe crushing chest pain"` in the chat. Verify the system triggers the immediate 911 / 988 emergency guidance without conversational delay.

