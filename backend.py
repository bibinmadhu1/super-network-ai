"""
SuperNetworkAI - FastAPI Backend
All business logic lives here. Uses Groq for AI features.
Run: uvicorn backend:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from groq import Groq
import json
import uuid
import re
from datetime import datetime

app = FastAPI(title="SuperNetworkAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory store (replace with a real DB in production)
# ---------------------------------------------------------------------------
USERS: dict[str, dict] = {}
MESSAGES: list[dict] = []
CONNECTION_REQUESTS: list[dict] = []
BLOCKED_PAIRS: set[tuple] = set()

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class IkigaiAnswers(BaseModel):
    love: str = Field("", description="What do you love doing?")
    good_at: str = Field("", description="What are you good at?")
    world_needs: str = Field("", description="What does the world need that you can offer?")
    paid_for: str = Field("", description="What can you be paid for?")

class SocialProfiles(BaseModel):
    linkedin: str = ""
    github: str = ""
    twitter: str = ""
    website: str = ""

class UserProfile(BaseModel):
    name: str
    email: str
    bio: str = ""
    ikigai: IkigaiAnswers = IkigaiAnswers()
    skills: List[str] = []
    interests: List[str] = []
    intent: Literal["cofounder", "teammate", "client", "open"] = "open"
    availability: Literal["full-time", "part-time", "weekends", "flexible"] = "flexible"
    working_style: str = ""
    social_profiles: SocialProfiles = SocialProfiles()
    portfolio_text: str = ""
    is_public: bool = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    ikigai: Optional[IkigaiAnswers] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    intent: Optional[Literal["cofounder", "teammate", "client", "open"]] = None
    availability: Optional[Literal["full-time", "part-time", "weekends", "flexible"]] = None
    working_style: Optional[str] = None
    social_profiles: Optional[SocialProfiles] = None
    portfolio_text: Optional[str] = None
    is_public: Optional[bool] = None

class CVImportRequest(BaseModel):
    cv_text: str
    groq_api_key: str

class SearchRequest(BaseModel):
    query: str
    current_user_id: str
    groq_api_key: str
    filter_intent: Optional[str] = None
    top_k: int = 10

class MessageRequest(BaseModel):
    sender_id: str
    receiver_id: str
    content: str

class ConnectionRequest(BaseModel):
    sender_id: str
    receiver_id: str
    message: str = ""

class BlockRequest(BaseModel):
    blocker_id: str
    blocked_id: str

class AIFillRequest(BaseModel):
    user_id: str
    groq_api_key: str

# ---------------------------------------------------------------------------
# Helper: Groq client factory
# ---------------------------------------------------------------------------

def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)

def profile_to_text(profile: dict) -> str:
    """Serialize a user profile into a plain-text description for LLM context."""
    ikigai = profile.get("ikigai", {})
    return f"""
Name: {profile.get('name', '')}
Bio: {profile.get('bio', '')}
Skills: {', '.join(profile.get('skills', []))}
Interests: {', '.join(profile.get('interests', []))}
Intent: {profile.get('intent', '')}
Availability: {profile.get('availability', '')}
Working Style: {profile.get('working_style', '')}
Portfolio: {profile.get('portfolio_text', '')}
Ikigai - Love: {ikigai.get('love', '')}
Ikigai - Good At: {ikigai.get('good_at', '')}
Ikigai - World Needs: {ikigai.get('world_needs', '')}
Ikigai - Paid For: {ikigai.get('paid_for', '')}
""".strip()

# ---------------------------------------------------------------------------
# User Endpoints
# ---------------------------------------------------------------------------

@app.post("/users/register", response_model=dict)
def register_user(profile: UserProfile):
    """Register a new user."""
    # Check for duplicate email
    for uid, u in USERS.items():
        if u["email"] == profile.email:
            raise HTTPException(status_code=400, detail="Email already registered.")
    uid = str(uuid.uuid4())
    USERS[uid] = {**profile.model_dump(), "id": uid, "created_at": datetime.utcnow().isoformat()}
    return {"user_id": uid, "message": "User registered successfully."}


@app.get("/users/{user_id}", response_model=dict)
def get_user(user_id: str):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")
    return USERS[user_id]


@app.patch("/users/{user_id}", response_model=dict)
def update_user(user_id: str, update: UserProfileUpdate):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")
    data = update.model_dump(exclude_none=True)
    # Handle nested models
    for key, val in data.items():
        if isinstance(val, dict) and key in USERS[user_id] and isinstance(USERS[user_id][key], dict):
            USERS[user_id][key].update(val)
        else:
            USERS[user_id][key] = val
    return {"message": "Profile updated.", "user": USERS[user_id]}


@app.get("/users", response_model=dict)
def list_users(requester_id: Optional[str] = Query(None)):
    """List all public users (excluding blocked relationships)."""
    visible = []
    for uid, u in USERS.items():
        if uid == requester_id:
            continue
        if requester_id and (
            (requester_id, uid) in BLOCKED_PAIRS or
            (uid, requester_id) in BLOCKED_PAIRS
        ):
            continue
        if u.get("is_public", True):
            visible.append(u)
    return {"users": visible, "total": len(visible)}


# ---------------------------------------------------------------------------
# CV / Portfolio Import
# ---------------------------------------------------------------------------

@app.post("/users/import-cv", response_model=dict)
def import_cv(req: CVImportRequest):
    """Use Groq to extract structured profile data from a CV/portfolio text."""
    client = get_groq_client(req.groq_api_key)
    prompt = f"""
You are a profile extraction assistant. Given the following CV or portfolio text, extract structured information and return ONLY a valid JSON object with these keys:
- name (string)
- bio (string, 2-3 sentences summary)
- skills (array of strings)
- interests (array of strings)
- working_style (string)
- portfolio_text (string, brief highlight of key projects/achievements)
- social_profiles (object with keys: linkedin, github, twitter, website — use empty string if not found)
- ikigai (object with keys: love, good_at, world_needs, paid_for — infer from CV)

CV Text:
{req.cv_text[:4000]}

Return ONLY the JSON object, no markdown, no explanation.
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"AI returned non-JSON output: {raw[:300]}")
    return {"extracted_profile": extracted}


# ---------------------------------------------------------------------------
# AI Pre-fill matchmaking criteria
# ---------------------------------------------------------------------------

@app.post("/users/{user_id}/ai-fill", response_model=dict)
def ai_fill_profile(user_id: str, req: AIFillRequest):
    """Use AI to suggest/update matchmaking criteria based on existing profile."""
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")
    user = USERS[user_id]
    client = get_groq_client(req.groq_api_key)
    prompt = f"""
You are a career and networking coach. Based on the following user profile, suggest enriched matchmaking criteria.
Return ONLY a valid JSON object with:
- skills (array of strings — add missing ones inferred from context)
- interests (array of strings)
- working_style (string)
- ikigai (object: love, good_at, world_needs, paid_for)

Profile:
{profile_to_text(user)}

Return ONLY JSON, no markdown.
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=800,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    try:
        suggestions = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="AI returned non-JSON output.")
    return {"suggestions": suggestions}


# ---------------------------------------------------------------------------
# AI-powered Natural Language Search & Matching
# ---------------------------------------------------------------------------

@app.post("/search", response_model=dict)
def search_matches(req: SearchRequest):
    """
    Natural language search. Uses Groq to score and explain matches.
    Returns ranked list with AI-generated summaries.
    """
    if req.current_user_id not in USERS:
        raise HTTPException(status_code=404, detail="Current user not found.")

    current_user = USERS[req.current_user_id]
    current_profile_text = profile_to_text(current_user)

    # Gather candidates (public, not blocked, not self)
    candidates = []
    for uid, u in USERS.items():
        if uid == req.current_user_id:
            continue
        if (req.current_user_id, uid) in BLOCKED_PAIRS or (uid, req.current_user_id) in BLOCKED_PAIRS:
            continue
        if not u.get("is_public", True):
            continue
        if req.filter_intent and u.get("intent") not in [req.filter_intent, "open"]:
            continue
        candidates.append(u)

    if not candidates:
        return {"matches": [], "total": 0}

    # Build candidate summaries for LLM context (limit to 15 to stay in context window)
    candidate_texts = []
    for c in candidates[:15]:
        candidate_texts.append(f"ID: {c['id']}\n{profile_to_text(c)}")

    candidates_block = "\n\n---\n\n".join(candidate_texts)

    client = get_groq_client(req.groq_api_key)
    prompt = f"""
You are an expert networking matchmaker for startup founders and professionals.

CURRENT USER:
{current_profile_text}

SEARCH QUERY: "{req.query}"

CANDIDATES:
{candidates_block}

Task: Score each candidate (0-100) for how well they match the current user's query and profile. Consider skills complementarity, shared interests, compatible working styles, intent alignment, and ikigai synergy.

Return ONLY a valid JSON array of objects, each with:
- id (string, the candidate's ID)
- score (integer 0-100)
- category (one of: "cofounder", "teammate", "client")
- summary (string, 2-3 sentences explaining why this is a great match — be specific, reference actual profile details)
- match_highlights (array of 3 short strings, key reasons for match)

Sort by score descending. Return top {min(req.top_k, len(candidates[:15]))} matches only. Return ONLY the JSON array.
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    try:
        ranked = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="AI returned non-JSON output for matches.")

    # Enrich with user profile data
    enriched = []
    for item in ranked:
        user_data = USERS.get(item.get("id", ""), {})
        if user_data:
            enriched.append({**item, "profile": user_data})

    return {"matches": enriched, "total": len(enriched), "query": req.query}


# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------

@app.post("/messages", response_model=dict)
def send_message(req: MessageRequest):
    if req.sender_id not in USERS:
        raise HTTPException(status_code=404, detail="Sender not found.")
    if req.receiver_id not in USERS:
        raise HTTPException(status_code=404, detail="Receiver not found.")
    if (req.sender_id, req.receiver_id) in BLOCKED_PAIRS or (req.receiver_id, req.sender_id) in BLOCKED_PAIRS:
        raise HTTPException(status_code=403, detail="Cannot send message to this user.")
    msg = {
        "id": str(uuid.uuid4()),
        "sender_id": req.sender_id,
        "receiver_id": req.receiver_id,
        "content": req.content,
        "timestamp": datetime.utcnow().isoformat(),
        "read": False,
    }
    MESSAGES.append(msg)
    return {"message_id": msg["id"], "status": "sent"}


@app.get("/messages/{user_id}", response_model=dict)
def get_messages(user_id: str, other_user_id: Optional[str] = Query(None)):
    """Get conversation messages for a user, optionally filtered by conversation partner."""
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")
    msgs = [
        m for m in MESSAGES
        if (m["sender_id"] == user_id or m["receiver_id"] == user_id)
        and (
            other_user_id is None or
            m["sender_id"] == other_user_id or
            m["receiver_id"] == other_user_id
        )
    ]
    # Mark as read
    for m in msgs:
        if m["receiver_id"] == user_id:
            m["read"] = True
    return {"messages": sorted(msgs, key=lambda x: x["timestamp"]), "total": len(msgs)}


@app.get("/messages/{user_id}/conversations", response_model=dict)
def get_conversations(user_id: str):
    """List all unique conversations for a user."""
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")
    partners = set()
    for m in MESSAGES:
        if m["sender_id"] == user_id:
            partners.add(m["receiver_id"])
        elif m["receiver_id"] == user_id:
            partners.add(m["sender_id"])

    convos = []
    for pid in partners:
        if pid not in USERS:
            continue
        thread = [
            m for m in MESSAGES
            if (m["sender_id"] == user_id and m["receiver_id"] == pid) or
               (m["sender_id"] == pid and m["receiver_id"] == user_id)
        ]
        last = sorted(thread, key=lambda x: x["timestamp"])[-1] if thread else None
        unread = sum(1 for m in thread if m["receiver_id"] == user_id and not m["read"])
        convos.append({
            "partner": USERS[pid],
            "last_message": last,
            "unread_count": unread,
        })

    convos.sort(key=lambda x: x["last_message"]["timestamp"] if x["last_message"] else "", reverse=True)
    return {"conversations": convos}


# ---------------------------------------------------------------------------
# Connection Requests
# ---------------------------------------------------------------------------

@app.post("/connections/request", response_model=dict)
def send_connection_request(req: ConnectionRequest):
    if req.sender_id not in USERS or req.receiver_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")
    # Check for duplicates
    for cr in CONNECTION_REQUESTS:
        if cr["sender_id"] == req.sender_id and cr["receiver_id"] == req.receiver_id and cr["status"] == "pending":
            raise HTTPException(status_code=400, detail="Connection request already pending.")
    cr = {
        "id": str(uuid.uuid4()),
        "sender_id": req.sender_id,
        "receiver_id": req.receiver_id,
        "message": req.message,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    CONNECTION_REQUESTS.append(cr)
    return {"request_id": cr["id"], "status": "sent"}


@app.get("/connections/{user_id}", response_model=dict)
def get_connections(user_id: str):
    sent = [cr for cr in CONNECTION_REQUESTS if cr["sender_id"] == user_id]
    received = [cr for cr in CONNECTION_REQUESTS if cr["receiver_id"] == user_id]
    # Enrich with profile data
    for cr in sent:
        cr["receiver_profile"] = USERS.get(cr["receiver_id"], {})
    for cr in received:
        cr["sender_profile"] = USERS.get(cr["sender_id"], {})
    return {"sent": sent, "received": received}


@app.patch("/connections/{request_id}", response_model=dict)
def respond_to_connection(request_id: str, action: Literal["accept", "decline"] = Query(...)):
    for cr in CONNECTION_REQUESTS:
        if cr["id"] == request_id:
            cr["status"] = action + "d"
            return {"message": f"Connection request {cr['status']}."}
    raise HTTPException(status_code=404, detail="Connection request not found.")


# ---------------------------------------------------------------------------
# Block / Visibility
# ---------------------------------------------------------------------------

@app.post("/users/block", response_model=dict)
def block_user(req: BlockRequest):
    BLOCKED_PAIRS.add((req.blocker_id, req.blocked_id))
    return {"message": f"User {req.blocked_id} has been blocked."}


@app.post("/users/unblock", response_model=dict)
def unblock_user(req: BlockRequest):
    BLOCKED_PAIRS.discard((req.blocker_id, req.blocked_id))
    return {"message": f"User {req.blocked_id} has been unblocked."}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "users": len(USERS), "messages": len(MESSAGES)}


# ---------------------------------------------------------------------------
# Dev Seed Data (optional helper)
# ---------------------------------------------------------------------------

@app.post("/dev/seed", response_model=dict)
def seed_data():
    """Seed some sample users for demo/testing."""
    samples = [
        {
            "name": "Aisha Patel", "email": "aisha@example.com",
            "bio": "Full-stack engineer passionate about social impact tech.",
            "ikigai": {"love": "Building products that connect people", "good_at": "React, Node.js, system design", "world_needs": "Accessible mental health tools", "paid_for": "Software engineering"},
            "skills": ["React", "Node.js", "PostgreSQL", "TypeScript", "System Design"],
            "interests": ["EdTech", "Mental Health", "Sustainability"],
            "intent": "cofounder", "availability": "full-time", "working_style": "Async-first, data-driven, open to debate",
            "social_profiles": {"linkedin": "linkedin.com/in/aisha", "github": "github.com/aisha", "twitter": "", "website": "aisha.dev"},
            "portfolio_text": "Led engineering at 3 YC-backed startups. Built a mental health app with 50k users.",
            "is_public": True,
        },
        {
            "name": "Marcus Rivera", "email": "marcus@example.com",
            "bio": "Growth marketer and brand strategist with a love for storytelling.",
            "ikigai": {"love": "Crafting compelling narratives", "good_at": "SEO, paid ads, content strategy", "world_needs": "Authentic brand voices", "paid_for": "Marketing consulting"},
            "skills": ["SEO", "Content Marketing", "Brand Strategy", "Paid Ads", "Analytics"],
            "interests": ["Future of Work", "Creator Economy", "Climate Tech"],
            "intent": "cofounder", "availability": "part-time", "working_style": "Collaborative, loves deep work blocks, morning person",
            "social_profiles": {"linkedin": "linkedin.com/in/marcus", "github": "", "twitter": "twitter.com/marcus", "website": ""},
            "portfolio_text": "Grew SaaS from 0 to $2M ARR. Managed $5M ad budget for Series B startup.",
            "is_public": True,
        },
        {
            "name": "Priya Nair", "email": "priya@example.com",
            "bio": "Product designer focused on human-centered, accessible design.",
            "ikigai": {"love": "Solving complex UX problems", "good_at": "Figma, design systems, user research", "world_needs": "Inclusive digital experiences", "paid_for": "UX/Product Design"},
            "skills": ["Figma", "User Research", "Design Systems", "Prototyping", "Accessibility"],
            "interests": ["HealthTech", "EdTech", "Fintech"],
            "intent": "teammate", "availability": "flexible", "working_style": "Visual thinker, thrives in structured sprints",
            "social_profiles": {"linkedin": "", "github": "", "twitter": "", "website": "priya.design"},
            "portfolio_text": "Redesigned onboarding for fintech app, reducing drop-off by 40%. Design lead at 2 startups.",
            "is_public": True,
        },
        {
            "name": "Jonas Weber", "email": "jonas@example.com",
            "bio": "AI/ML engineer building recommendation and NLP systems.",
            "ikigai": {"love": "Teaching machines to understand context", "good_at": "PyTorch, LLMs, MLOps", "world_needs": "Trustworthy AI systems", "paid_for": "Machine learning consulting"},
            "skills": ["Python", "PyTorch", "LLMs", "MLOps", "Data Engineering"],
            "interests": ["AI Safety", "Open Source", "Distributed Systems"],
            "intent": "cofounder", "availability": "weekends", "working_style": "Deep focus, prefers written communication",
            "social_profiles": {"linkedin": "", "github": "github.com/jonas", "twitter": "", "website": ""},
            "portfolio_text": "Published 3 papers on NLP. Built recommendation engine serving 10M users.",
            "is_public": True,
        },
        {
            "name": "Sofia Chen", "email": "sofia@example.com",
            "bio": "Operations and finance lead who turns chaos into scalable systems.",
            "ikigai": {"love": "Building operational clarity", "good_at": "Financial modeling, process design, fundraising", "world_needs": "Better-run mission-driven companies", "paid_for": "COO / Operations consulting"},
            "skills": ["Financial Modeling", "Fundraising", "Operations", "OKRs", "Hiring"],
            "interests": ["Climate Tech", "Social Enterprise", "Future of Finance"],
            "intent": "client", "availability": "full-time", "working_style": "Systems thinker, detail-oriented, direct communicator",
            "social_profiles": {"linkedin": "linkedin.com/in/sofia", "github": "", "twitter": "", "website": ""},
            "portfolio_text": "CFO at Series A. Raised $12M in two rounds. Built OKR systems adopted company-wide.",
            "is_public": True,
        },
    ]
    added = []
    for s in samples:
        uid = str(uuid.uuid4())
        USERS[uid] = {**s, "id": uid, "created_at": datetime.utcnow().isoformat(),
                      "ikigai": s["ikigai"], "social_profiles": s["social_profiles"]}
        added.append(uid)
    return {"message": f"Seeded {len(added)} users.", "user_ids": added}
