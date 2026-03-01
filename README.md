# SuperNetworkAI 🔗

AI-Powered Networking to Find Cofounders, Teams & Clients

---

## Recommended Hosting Stack (both free)

| Layer | Service | Why |
|-------|---------|-----|
| **Backend** (FastAPI) | [Render.com](https://render.com) | Free web service, auto-deploys from GitHub, zero config needed |
| **Frontend** (Streamlit) | [Streamlit Cloud](https://streamlit.io/cloud) | Free, built for Streamlit, deploys straight from GitHub |

---

## Local Development

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# .env already points to http://localhost:8000 — no changes needed locally
```

### 3. Run backend
```bash
uvicorn backend:app --reload --port 8000
# API docs → http://localhost:8000/docs
```

### 4. Run frontend (new terminal)
```bash
streamlit run app.py
# Opens → http://localhost:8501
```

### 5. Add Groq API key
Get a free key at https://console.groq.com and paste it into the sidebar.

### 6. Seed demo data (optional)
Click **"Seed Sample Users"** on the home page.

---

## Deploying to Production

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/supernetworkai.git
git push -u origin main
```

### Step 2 — Deploy Backend on Render.com (free)

1. Go to [render.com](https://render.com) and sign up / log in
2. Click **New** → **Blueprint**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` → click **Apply**
5. Wait ~2 minutes for the build to finish
6. Copy your live URL, e.g. `https://supernetworkai-backend.onrender.com`

> **Free tier note:** Render free services spin down after 15 min of inactivity.
> The first request after sleep takes ~30s to wake up. Fine for demos.
> Upgrade to the $7/mo Starter plan to keep it always-on.

### Step 3 — Deploy Frontend on Streamlit Cloud (free)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Select your repo, branch `main`, file `app.py`
4. Click **Advanced settings** → **Secrets** and paste:
   ```toml
   BACKEND_URL = "https://supernetworkai-backend.onrender.com"
   ```
   Replace with your actual Render URL from Step 2.
5. Click **Deploy** — your app goes live at `https://YOUR-APP.streamlit.app`

---

## Environment Configuration Summary

The frontend resolves `BACKEND_URL` in this priority order — **no code changes needed**:

```
1. st.secrets["BACKEND_URL"]   ← Streamlit Cloud secrets  (production)
2. os.environ["BACKEND_URL"]   ← .env file / system env   (local / Docker)
3. http://localhost:8000        ← hardcoded fallback        (bare local dev)
```

---

## Project Structure

```
supernetworkai/
├── backend.py              # FastAPI — all business logic & AI
├── app.py                  # Streamlit — UI only, calls backend via HTTP
├── requirements.txt
├── render.yaml             # Render.com one-click deploy config
├── .env.example            # Copy to .env for local dev
├── .gitignore
└── .streamlit/
    ├── config.toml         # Streamlit theme
    └── secrets.toml        # Local secrets (git-ignored)
```

---

## API Reference

Full interactive docs at `YOUR_BACKEND_URL/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/register` | Register new user |
| GET | `/users/{id}` | Get user profile |
| PATCH | `/users/{id}` | Update profile |
| GET | `/users` | List public users |
| POST | `/users/import-cv` | AI extract from CV text |
| POST | `/users/{id}/ai-fill` | AI enhance profile |
| POST | `/search` | NL search with AI ranking |
| POST | `/messages` | Send message |
| GET | `/messages/{id}/conversations` | List conversations |
| POST | `/connections/request` | Send connection request |
| PATCH | `/connections/{id}?action=accept\|decline` | Respond to request |
| POST | `/users/block` | Block a user |
| POST | `/dev/seed` | Seed demo users |
| GET | `/health` | Health check |

---

## Notes

- **Storage:** In-memory — data resets on restart. For persistence, Render also offers a free PostgreSQL instance.
- **Groq key:** Passed per-request from the frontend sidebar — never stored server-side.
- **Model:** `llama3-70b-8192` via Groq.
