# SuperNetworkAI 🔗

AI-Powered Networking to Find Cofounders, Teams & Clients

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the FastAPI backend
```bash
uvicorn backend:app --reload --port 8000
```
API docs available at: http://localhost:8000/docs

### 3. Start the Streamlit frontend (new terminal)
```bash
streamlit run app.py
```
Opens at: http://localhost:8501

### 4. Get a Groq API Key
- Sign up at https://console.groq.com
- Create an API key (it's free)
- Enter it in the sidebar of the app

### 5. Seed demo data (optional)
Click **"Seed Sample Users"** on the home page to add 5 realistic demo profiles.

---

## Features

| Feature | Status |
|---|---|
| Ikigai-based onboarding | ✅ |
| CV/portfolio text import via AI | ✅ |
| AI profile enhancement (pre-fill) | ✅ |
| Natural language search | ✅ |
| AI-ranked matches with explanations | ✅ |
| Match categorization (cofounder/teammate/client) | ✅ |
| In-app messaging | ✅ |
| Connection requests (accept/decline) | ✅ |
| Public/private profile toggle | ✅ |
| Block users | ✅ |
| Profile export (JSON) | ✅ |
| Web-only, minimalist dark UI | ✅ |

## Architecture

```
┌─────────────────┐         ┌──────────────────────────┐
│  Streamlit UI   │ ──────► │  FastAPI Backend          │
│  app.py         │  HTTP   │  backend.py               │
│                 │         │                          │
│  - Auth/Login   │         │  - User CRUD             │
│  - Onboarding   │         │  - AI-powered search     │
│  - Search UI    │         │  - CV import             │
│  - Messages     │         │  - Profile enhancement   │
│  - Connections  │         │  - Messaging             │
└─────────────────┘         │  - Connection requests   │
                             │  - Block/visibility      │
                             └──────────┬───────────────┘
                                        │
                                        ▼
                             ┌──────────────────────────┐
                             │  Groq API (llama3-70b)   │
                             │  - Natural language match │
                             │  - CV extraction         │
                             │  - Profile AI-fill       │
                             └──────────────────────────┘
```

## API Endpoints

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
| GET | `/messages/{id}` | Get messages |
| GET | `/messages/{id}/conversations` | List conversations |
| POST | `/connections/request` | Send connection request |
| GET | `/connections/{id}` | Get connections |
| PATCH | `/connections/{req_id}` | Accept/decline request |
| POST | `/users/block` | Block a user |
| POST | `/users/unblock` | Unblock a user |
| POST | `/dev/seed` | Seed demo users |
| GET | `/health` | Health check |

## Notes

- This demo uses in-memory storage. Restart the backend to clear all data.
- For production: replace the `USERS`, `MESSAGES`, etc. dicts with a real database (PostgreSQL recommended).
- The Groq API key is passed per-request from the frontend — never stored server-side.
- Model used: `llama3-70b-8192` via Groq (fast, capable, free tier available)
