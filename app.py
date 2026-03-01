"""
SuperNetworkAI - Streamlit Frontend
Run: streamlit run app.py
Make sure backend is running on http://localhost:8000
"""

import streamlit as st
import requests
import json
from datetime import datetime

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
API = "http://localhost:8000"

st.set_page_config(
    page_title="SuperNetworkAI",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Dark editorial aesthetic
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* Root palette */
:root {
  --bg: #0d0f14;
  --surface: #161920;
  --surface2: #1e2230;
  --border: #2a2f3e;
  --accent: #6ee7b7;
  --accent2: #818cf8;
  --warn: #f59e0b;
  --danger: #f87171;
  --text: #e2e8f0;
  --muted: #64748b;
  --radius: 12px;
}

/* Global */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 4rem; max-width: 1200px; }

/* Headings */
h1, h2, h3, h4 {
  font-family: 'DM Serif Display', serif;
  color: var(--text);
  letter-spacing: -0.02em;
}
h1 { font-size: 2.8rem; line-height: 1.1; }
h2 { font-size: 1.8rem; }
h3 { font-size: 1.3rem; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  font-size: 1rem !important;
  color: var(--muted) !important;
  font-family: 'DM Sans', sans-serif !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Buttons */
.stButton > button {
  background: var(--accent) !important;
  color: #0d0f14 !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
  padding: 0.5rem 1.2rem !important;
  transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stSelectbox select {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(110,231,183,0.15) !important;
}

/* Expander */
details {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 0.2rem 0.5rem;
}
details summary { color: var(--text) !important; cursor: pointer; }

/* Metric */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem !important;
}

/* Match cards — custom HTML components */
.match-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
  transition: border-color 0.2s;
}
.match-card:hover { border-color: var(--accent); }
.match-card .score-badge {
  display: inline-block;
  background: var(--accent);
  color: #0d0f14;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 0.2rem 0.6rem;
  border-radius: 100px;
  margin-right: 0.5rem;
}
.match-card .category-badge {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--accent2);
  color: var(--accent2);
  font-size: 0.78rem;
  font-weight: 500;
  padding: 0.2rem 0.6rem;
  border-radius: 100px;
}
.match-card .name { font-family: 'DM Serif Display', serif; font-size: 1.15rem; margin: 0.4rem 0 0.2rem; }
.match-card .bio { color: var(--muted); font-size: 0.9rem; }
.match-card .summary { font-style: italic; color: #94a3b8; margin: 0.5rem 0; font-size: 0.9rem; border-left: 3px solid var(--accent); padding-left: 0.8rem; }
.match-card .highlights { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.match-card .highlight-pill {
  background: rgba(110,231,183,0.1);
  color: var(--accent);
  font-size: 0.78rem;
  padding: 0.15rem 0.55rem;
  border-radius: 100px;
  border: 1px solid rgba(110,231,183,0.2);
}

/* Message bubbles */
.msg-bubble-right {
  background: var(--accent);
  color: #0d0f14;
  border-radius: 16px 16px 4px 16px;
  padding: 0.6rem 1rem;
  margin: 0.3rem 0 0.3rem 20%;
  font-size: 0.9rem;
}
.msg-bubble-left {
  background: var(--surface2);
  color: var(--text);
  border-radius: 16px 16px 16px 4px;
  padding: 0.6rem 1rem;
  margin: 0.3rem 20% 0.3rem 0;
  font-size: 0.9rem;
  border: 1px solid var(--border);
}
.msg-time { font-size: 0.72rem; color: var(--muted); margin-bottom: 0.1rem; }

/* Tag pills */
.skill-pill {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 0.78rem;
  padding: 0.15rem 0.55rem;
  border-radius: 100px;
  margin: 0.15rem;
}

/* Intent badge */
.intent-cofounder { color: #6ee7b7; border-color: #6ee7b7; background: rgba(110,231,183,0.1); }
.intent-teammate { color: #818cf8; border-color: #818cf8; background: rgba(129,140,248,0.1); }
.intent-client { color: #f59e0b; border-color: #f59e0b; background: rgba(245,158,11,0.1); }
.intent-open { color: #e2e8f0; border-color: #2a2f3e; background: #1e2230; }

/* Logo */
.app-logo {
  font-family: 'DM Serif Display', serif;
  font-size: 1.6rem;
  letter-spacing: -0.03em;
  color: var(--accent);
}
.app-logo span { color: var(--accent2); }

/* Divider */
hr { border-color: var(--border) !important; margin: 1.5rem 0; }

/* Info/success/warning boxes */
.stInfo, .stSuccess, .stWarning, .stError {
  border-radius: var(--radius) !important;
  border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
def init_state():
    defaults = {
        "user_id": None,
        "user_profile": None,
        "groq_api_key": "",
        "page": "home",
        "search_results": [],
        "active_chat": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ──────────────────────────────────────────────
# API helpers
# ──────────────────────────────────────────────
def api_get(path, params=None):
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_post(path, data):
    try:
        r = requests.post(f"{API}{path}", json=data, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend.")
        return None
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        st.error(f"Error: {detail or str(e)}")
        return None

def api_patch(path, data):
    try:
        r = requests.patch(f"{API}{path}", json=data, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def refresh_profile():
    if st.session_state.user_id:
        p = api_get(f"/users/{st.session_state.user_id}")
        if p:
            st.session_state.user_profile = p

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="app-logo">Super<span>Network</span>AI</div>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Professional Networking*")
    st.divider()

    if not st.session_state.user_id:
        st.markdown("### Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
        if st.button("📝 Register", use_container_width=True):
            st.session_state.page = "register"
        if st.button("🔑 Login", use_container_width=True):
            st.session_state.page = "login"
    else:
        profile = st.session_state.user_profile or {}
        st.markdown(f"**{profile.get('name', 'User')}**")
        intent = profile.get('intent', 'open')
        intent_colors = {"cofounder": "🟢", "teammate": "🟣", "client": "🟡", "open": "⚪"}
        st.caption(f"{intent_colors.get(intent, '⚪')} Looking for: {intent.title()}")
        st.divider()

        st.markdown("### Menu")
        pages = [
            ("🔍", "Search", "search"),
            ("👥", "Discover", "discover"),
            ("👤", "My Profile", "profile"),
            ("💬", "Messages", "messages"),
            ("🔗", "Connections", "connections"),
            ("⚙️", "Settings", "settings"),
        ]
        for icon, label, page_key in pages:
            if st.button(f"{icon} {label}", use_container_width=True):
                st.session_state.page = page_key

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_profile = None
            st.session_state.page = "home"
            st.rerun()

    st.divider()
    st.markdown("### Groq API Key")
    key = st.text_input("API Key", value=st.session_state.groq_api_key, type="password", key="groq_key_input", placeholder="gsk_...")
    if key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = key
    if not st.session_state.groq_api_key:
        st.caption("⚠️ Required for AI features.")


# ──────────────────────────────────────────────
# PAGE: HOME
# ──────────────────────────────────────────────
def page_home():
    st.markdown("# SuperNetworkAI")
    st.markdown("### *Find your cofounder, team & clients with AI.*")
    st.markdown("""
    SuperNetworkAI uses large language models to intelligently match you with the right people —
    based on your **Ikigai**, skills, intent, and working style.
    Not another LinkedIn. Not a directory. An intelligent network.
    """)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("✨ AI-Powered Matches", "Ranked & Explained")
    with c2:
        st.metric("🧭 Ikigai Onboarding", "Purpose-Driven Profiles")
    with c3:
        st.metric("💬 In-App Messaging", "Connect Directly")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Get Started — Register", use_container_width=True):
            st.session_state.page = "register"
    with col2:
        if st.button("🔑 I Already Have an Account", use_container_width=True):
            st.session_state.page = "login"

    st.divider()
    st.markdown("#### How it works")
    cols = st.columns(4)
    steps = [
        ("1", "Complete your Ikigai profile", "Answer 4 questions about purpose, skills, and what the world needs."),
        ("2", "AI enriches your profile", "Our AI suggests skills, interests, and matchmaking criteria."),
        ("3", "Natural language search", "Describe who you're looking for in plain English."),
        ("4", "AI-ranked matches", "Get a ranked list with AI summaries explaining each match."),
    ]
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"**{num}.** {title}")
            st.caption(desc)

    # Seed data button (dev helper)
    st.divider()
    st.caption("🧪 Demo Mode")
    if st.button("Seed Sample Users (for demo)", use_container_width=False):
        r = api_post("/dev/seed", {})
        if r:
            st.success(f"✅ {r['message']}")


# ──────────────────────────────────────────────
# PAGE: REGISTER
# ──────────────────────────────────────────────
def page_register():
    st.markdown("## Create Your Profile")
    st.caption("Tell us about yourself. Our AI will help fill in the gaps.")

    tab_manual, tab_cv = st.tabs(["✍️ Manual Entry", "📄 Import from CV / Portfolio"])

    with tab_manual:
        with st.form("register_form"):
            st.markdown("#### Basic Info")
            c1, c2 = st.columns(2)
            name = c1.text_input("Full Name *", placeholder="Jane Doe")
            email = c2.text_input("Email *", placeholder="jane@example.com")
            bio = st.text_area("Bio (2-3 sentences)", placeholder="What's your story?", height=80)

            st.markdown("#### Ikigai — Your Purpose")
            st.caption("Ikigai is the intersection of what you love, what you're good at, what the world needs, and what you can be paid for.")
            c1, c2 = st.columns(2)
            love = c1.text_area("What do you **love** doing?", height=80, placeholder="e.g. Building products that solve real problems")
            good_at = c2.text_area("What are you **good at**?", height=80, placeholder="e.g. Python, system design, storytelling")
            world_needs = c1.text_area("What does the **world need** that you can offer?", height=80, placeholder="e.g. Better mental health tools")
            paid_for = c2.text_area("What can you be **paid for**?", height=80, placeholder="e.g. Software engineering, consulting")

            st.markdown("#### Skills & Interests")
            skills_raw = st.text_input("Skills (comma-separated)", placeholder="React, Python, Design, Marketing")
            interests_raw = st.text_input("Interests (comma-separated)", placeholder="HealthTech, Climate, EdTech")

            st.markdown("#### Working Preferences")
            c1, c2, c3 = st.columns(3)
            intent = c1.selectbox("I'm looking for", ["cofounder", "teammate", "client", "open"])
            availability = c2.selectbox("Availability", ["full-time", "part-time", "weekends", "flexible"])
            working_style = c3.text_input("Working style", placeholder="e.g. Async-first, data-driven")

            st.markdown("#### Social Profiles")
            c1, c2, c3, c4 = st.columns(4)
            linkedin = c1.text_input("LinkedIn URL")
            github = c2.text_input("GitHub URL")
            twitter = c3.text_input("Twitter URL")
            website = c4.text_input("Website / Portfolio")

            portfolio_text = st.text_area("Portfolio highlights / key projects", height=80, placeholder="Briefly describe your most relevant work...")
            is_public = st.checkbox("Make my profile public", value=True)

            submitted = st.form_submit_button("🚀 Create Profile", use_container_width=True)

        if submitted:
            if not name or not email:
                st.error("Name and email are required.")
            else:
                payload = {
                    "name": name, "email": email, "bio": bio,
                    "ikigai": {"love": love, "good_at": good_at, "world_needs": world_needs, "paid_for": paid_for},
                    "skills": [s.strip() for s in skills_raw.split(",") if s.strip()],
                    "interests": [i.strip() for i in interests_raw.split(",") if i.strip()],
                    "intent": intent, "availability": availability, "working_style": working_style,
                    "social_profiles": {"linkedin": linkedin, "github": github, "twitter": twitter, "website": website},
                    "portfolio_text": portfolio_text, "is_public": is_public,
                }
                r = api_post("/users/register", payload)
                if r:
                    st.session_state.user_id = r["user_id"]
                    refresh_profile()
                    st.success("✅ Profile created! Welcome to SuperNetworkAI.")
                    st.session_state.page = "profile"
                    st.rerun()

    with tab_cv:
        st.markdown("Paste your CV text or portfolio description below. AI will extract and pre-fill your profile.")
        cv_text = st.text_area("CV / Portfolio Text", height=250, placeholder="Paste your CV, LinkedIn bio, or portfolio description here...")
        if st.button("🤖 Extract Profile with AI", use_container_width=True):
            if not st.session_state.groq_api_key:
                st.error("Please enter your Groq API key in the sidebar.")
            elif not cv_text.strip():
                st.error("Please paste some text.")
            else:
                with st.spinner("AI is extracting your profile..."):
                    r = api_post("/users/import-cv", {"cv_text": cv_text, "groq_api_key": st.session_state.groq_api_key})
                if r:
                    ext = r["extracted_profile"]
                    st.success("✅ Profile extracted! Review below and confirm to register.")
                    st.json(ext)
                    if st.button("✅ Register with this profile"):
                        # Need email — ask for it
                        st.session_state["cv_extracted"] = ext
                        st.info("Enter your email to complete registration:")
                        email_cv = st.text_input("Email *", key="cv_email")
                        if st.button("Complete Registration"):
                            payload = {**ext, "email": email_cv}
                            # Normalize nested objects
                            if isinstance(payload.get("ikigai"), dict):
                                pass  # already a dict
                            r2 = api_post("/users/register", payload)
                            if r2:
                                st.session_state.user_id = r2["user_id"]
                                refresh_profile()
                                st.session_state.page = "profile"
                                st.rerun()


# ──────────────────────────────────────────────
# PAGE: LOGIN (simple — pick from existing users)
# ──────────────────────────────────────────────
def page_login():
    st.markdown("## Sign In")
    st.caption("No password system in this demo — identify by email.")

    with st.form("login_form"):
        email = st.text_input("Your email", placeholder="jane@example.com")
        submitted = st.form_submit_button("Login")

    if submitted and email:
        users_data = api_get("/users")
        if users_data:
            all_users = users_data.get("users", [])
            # Also include non-public by checking directly
            match = None
            for u in all_users:
                if u.get("email", "").lower() == email.lower():
                    match = u
                    break
            if not match:
                # Try fetching all (including private) — for demo, just iterate
                st.error("No account found with that email. Please register first.")
            else:
                st.session_state.user_id = match["id"]
                st.session_state.user_profile = match
                st.success(f"✅ Welcome back, {match['name']}!")
                st.session_state.page = "search"
                st.rerun()


# ──────────────────────────────────────────────
# PAGE: PROFILE
# ──────────────────────────────────────────────
def page_profile():
    refresh_profile()
    profile = st.session_state.user_profile
    if not profile:
        st.error("Profile not found.")
        return

    st.markdown(f"## {profile['name']}")
    ikigai = profile.get("ikigai", {})
    social = profile.get("social_profiles", {})
    intent = profile.get("intent", "open")

    # Social links
    links = []
    for platform, url in social.items():
        if url:
            links.append(f"[{platform.title()}]({url if url.startswith('http') else 'https://' + url})")
    if links:
        st.markdown(" · ".join(links))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"*{profile.get('bio', '')}*")
        if profile.get("portfolio_text"):
            st.markdown("**Portfolio**")
            st.markdown(profile["portfolio_text"])
    with col2:
        intent_icon = {"cofounder": "🟢", "teammate": "🟣", "client": "🟡", "open": "⚪"}.get(intent, "⚪")
        st.metric("Intent", f"{intent_icon} {intent.title()}")
        st.metric("Availability", profile.get("availability", "—").title())

    # Skills
    if profile.get("skills"):
        st.markdown("**Skills**")
        skills_html = " ".join([f'<span class="skill-pill">{s}</span>' for s in profile["skills"]])
        st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)
        st.markdown("")

    # Interests
    if profile.get("interests"):
        st.markdown("**Interests**")
        interests_html = " ".join([f'<span class="skill-pill">{i}</span>' for i in profile["interests"]])
        st.markdown(f'<div>{interests_html}</div>', unsafe_allow_html=True)
        st.markdown("")

    # Ikigai
    with st.expander("🧭 Ikigai Answers"):
        c1, c2 = st.columns(2)
        c1.markdown(f"**Love:** {ikigai.get('love', '—')}")
        c2.markdown(f"**Good At:** {ikigai.get('good_at', '—')}")
        c1.markdown(f"**World Needs:** {ikigai.get('world_needs', '—')}")
        c2.markdown(f"**Paid For:** {ikigai.get('paid_for', '—')}")

    st.divider()

    # AI Fill
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🤖 AI-Enhance My Profile", use_container_width=True):
            if not st.session_state.groq_api_key:
                st.error("Groq API key required.")
            else:
                with st.spinner("AI is enhancing your profile..."):
                    r = api_post(f"/users/{st.session_state.user_id}/ai-fill",
                                 {"user_id": st.session_state.user_id, "groq_api_key": st.session_state.groq_api_key})
                if r:
                    suggestions = r["suggestions"]
                    st.success("✅ AI suggestions ready! Apply below.")
                    st.json(suggestions)
                    if st.button("✅ Apply AI Suggestions"):
                        api_patch(f"/users/{st.session_state.user_id}", suggestions)
                        refresh_profile()
                        st.success("Profile updated!")
                        st.rerun()

    # Edit profile
    with st.expander("✏️ Edit Profile"):
        with st.form("edit_profile"):
            new_bio = st.text_area("Bio", value=profile.get("bio", ""), height=80)
            new_skills = st.text_input("Skills (comma-separated)", value=", ".join(profile.get("skills", [])))
            new_interests = st.text_input("Interests (comma-separated)", value=", ".join(profile.get("interests", [])))
            new_intent = st.selectbox("Looking for", ["cofounder", "teammate", "client", "open"],
                                      index=["cofounder", "teammate", "client", "open"].index(profile.get("intent", "open")))
            new_avail = st.selectbox("Availability", ["full-time", "part-time", "weekends", "flexible"],
                                     index=["full-time", "part-time", "weekends", "flexible"].index(profile.get("availability", "flexible")))
            new_style = st.text_input("Working Style", value=profile.get("working_style", ""))
            new_public = st.checkbox("Public Profile", value=profile.get("is_public", True))
            if st.form_submit_button("Save Changes"):
                updates = {
                    "bio": new_bio,
                    "skills": [s.strip() for s in new_skills.split(",") if s.strip()],
                    "interests": [i.strip() for i in new_interests.split(",") if i.strip()],
                    "intent": new_intent,
                    "availability": new_avail,
                    "working_style": new_style,
                    "is_public": new_public,
                }
                r = api_patch(f"/users/{st.session_state.user_id}", updates)
                if r:
                    refresh_profile()
                    st.success("✅ Profile updated!")
                    st.rerun()


# ──────────────────────────────────────────────
# PAGE: SEARCH
# ──────────────────────────────────────────────
def page_search():
    st.markdown("## Find Your Match")
    st.caption("Describe who you're looking for in plain English. AI handles the rest.")

    if not st.session_state.groq_api_key:
        st.warning("⚠️ Enter your Groq API key in the sidebar to use AI-powered search.")

    c1, c2, c3 = st.columns([4, 1, 1])
    with c1:
        query = st.text_input("", placeholder="e.g. 'a technical cofounder who loves AI and sustainability' or 'a designer for a fintech startup'",
                              label_visibility="collapsed")
    with c2:
        filter_intent = st.selectbox("Role", ["any", "cofounder", "teammate", "client"], label_visibility="collapsed")
    with c3:
        search_btn = st.button("🔍 Search", use_container_width=True)

    if search_btn or (query and st.session_state.search_results):
        if search_btn and query:
            if not st.session_state.groq_api_key:
                st.error("Groq API key required for AI search.")
            else:
                with st.spinner("🤖 AI is finding and ranking your matches..."):
                    payload = {
                        "query": query,
                        "current_user_id": st.session_state.user_id,
                        "groq_api_key": st.session_state.groq_api_key,
                        "filter_intent": None if filter_intent == "any" else filter_intent,
                        "top_k": 10,
                    }
                    r = api_post("/search", payload)
                if r:
                    st.session_state.search_results = r.get("matches", [])

        render_match_results(st.session_state.search_results, query or "")


def render_match_results(matches, query):
    if not matches:
        st.info("No matches found. Try a different query or seed some demo users.")
        return

    st.markdown(f"#### {len(matches)} matches found")

    for m in matches:
        profile = m.get("profile", {})
        score = m.get("score", 0)
        category = m.get("category", "teammate")
        summary = m.get("summary", "")
        highlights = m.get("match_highlights", [])

        skills_html = " ".join([f'<span class="skill-pill">{s}</span>' for s in profile.get("skills", [])[:6]])
        highlights_html = " ".join([f'<span class="highlight-pill">✓ {h}</span>' for h in highlights])

        card_html = f"""
<div class="match-card">
  <div>
    <span class="score-badge">{score}%</span>
    <span class="category-badge intent-{category}">{category.upper()}</span>
  </div>
  <div class="name">{profile.get('name', 'Unknown')}</div>
  <div class="bio">{profile.get('bio', '')}</div>
  <div class="summary">{summary}</div>
  <div>{skills_html}</div>
  <div class="highlights">{highlights_html}</div>
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button(f"💬 Message", key=f"msg_{profile['id']}"):
                st.session_state.active_chat = profile["id"]
                st.session_state.page = "messages"
                st.rerun()
        with col2:
            if st.button(f"🔗 Connect", key=f"conn_{profile['id']}"):
                r = api_post("/connections/request", {
                    "sender_id": st.session_state.user_id,
                    "receiver_id": profile["id"],
                    "message": f"Hi {profile.get('name', '')}! I found you through AI search for '{query[:60]}'. Would love to connect!",
                })
                if r:
                    st.success(f"Connection request sent to {profile.get('name')}!")


# ──────────────────────────────────────────────
# PAGE: DISCOVER (browse all users)
# ──────────────────────────────────────────────
def page_discover():
    st.markdown("## Discover Members")

    data = api_get("/users", params={"requester_id": st.session_state.user_id})
    if not data:
        return

    users = data.get("users", [])
    if not users:
        st.info("No other members yet. Seed some demo users from the home page.")
        return

    # Filter controls
    c1, c2 = st.columns(2)
    intent_filter = c1.selectbox("Filter by intent", ["all", "cofounder", "teammate", "client", "open"])
    avail_filter = c2.selectbox("Filter by availability", ["all", "full-time", "part-time", "weekends", "flexible"])

    filtered = [
        u for u in users
        if (intent_filter == "all" or u.get("intent") == intent_filter)
        and (avail_filter == "all" or u.get("availability") == avail_filter)
    ]

    st.markdown(f"**{len(filtered)} members**")
    st.divider()

    for u in filtered:
        intent = u.get("intent", "open")
        intent_icon = {"cofounder": "🟢", "teammate": "🟣", "client": "🟡", "open": "⚪"}.get(intent, "⚪")
        skills_html = " ".join([f'<span class="skill-pill">{s}</span>' for s in u.get("skills", [])[:5]])

        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{u['name']}** &nbsp; {intent_icon} *{intent.title()}*")
                st.caption(u.get("bio", ""))
                st.markdown(f'<div style="margin-bottom:0.3rem">{skills_html}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("💬", key=f"disc_msg_{u['id']}", help="Message"):
                    st.session_state.active_chat = u["id"]
                    st.session_state.page = "messages"
                    st.rerun()
                if st.button("🔗", key=f"disc_conn_{u['id']}", help="Connect"):
                    r = api_post("/connections/request", {
                        "sender_id": st.session_state.user_id,
                        "receiver_id": u["id"],
                        "message": "",
                    })
                    if r:
                        st.success(f"Request sent to {u['name']}!")
            st.divider()


# ──────────────────────────────────────────────
# PAGE: MESSAGES
# ──────────────────────────────────────────────
def page_messages():
    st.markdown("## Messages")

    convos_data = api_get(f"/messages/{st.session_state.user_id}/conversations")
    if not convos_data:
        return

    convos = convos_data.get("conversations", [])

    col_list, col_chat = st.columns([1, 2])

    with col_list:
        st.markdown("#### Conversations")
        if not convos and not st.session_state.active_chat:
            st.info("No conversations yet. Find someone and message them!")

        for conv in convos:
            partner = conv["partner"]
            unread = conv.get("unread_count", 0)
            last = conv.get("last_message", {})
            is_active = st.session_state.active_chat == partner["id"]
            label = f"{'🔵 ' if unread else ''}**{partner['name']}**"
            if last:
                preview = last.get("content", "")[:40]
                label += f"\n{preview}…"
            if st.button(label, key=f"conv_{partner['id']}", use_container_width=True):
                st.session_state.active_chat = partner["id"]
                st.rerun()

        # Start new chat
        st.divider()
        st.markdown("#### New Message")
        users_data = api_get("/users", params={"requester_id": st.session_state.user_id})
        if users_data:
            other_users = {u["name"]: u["id"] for u in users_data.get("users", [])}
            if other_users:
                target_name = st.selectbox("To:", list(other_users.keys()), key="new_msg_target")
                if st.button("Open Chat", use_container_width=True):
                    st.session_state.active_chat = other_users[target_name]
                    st.rerun()

    with col_chat:
        if not st.session_state.active_chat:
            st.markdown("<br><br><center>← Select a conversation</center>", unsafe_allow_html=True)
            return

        partner_data = api_get(f"/users/{st.session_state.active_chat}")
        if not partner_data:
            return

        st.markdown(f"#### Chat with {partner_data.get('name', '')}")

        msgs_data = api_get(f"/messages/{st.session_state.user_id}",
                            params={"other_user_id": st.session_state.active_chat})
        if not msgs_data:
            return

        msgs = msgs_data.get("messages", [])

        # Message display
        chat_container = st.container()
        with chat_container:
            if not msgs:
                st.caption("No messages yet. Say hello!")
            for msg in msgs:
                is_mine = msg["sender_id"] == st.session_state.user_id
                time_str = msg["timestamp"][:16].replace("T", " ")
                if is_mine:
                    st.markdown(f'<div class="msg-time" style="text-align:right">{time_str}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="msg-bubble-right">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="msg-time">{partner_data.get("name", "")}, {time_str}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="msg-bubble-left">{msg["content"]}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("send_msg_form", clear_on_submit=True):
            msg_content = st.text_input("", placeholder=f"Message {partner_data.get('name', '')}...", label_visibility="collapsed")
            send = st.form_submit_button("Send →", use_container_width=True)
        if send and msg_content.strip():
            r = api_post("/messages", {
                "sender_id": st.session_state.user_id,
                "receiver_id": st.session_state.active_chat,
                "content": msg_content,
            })
            if r:
                st.rerun()


# ──────────────────────────────────────────────
# PAGE: CONNECTIONS
# ──────────────────────────────────────────────
def page_connections():
    st.markdown("## Connections")

    data = api_get(f"/connections/{st.session_state.user_id}")
    if not data:
        return

    received = data.get("received", [])
    sent = data.get("sent", [])

    pending_received = [r for r in received if r["status"] == "pending"]
    if pending_received:
        st.markdown(f"#### 🔔 {len(pending_received)} Pending Request(s)")
        for req in pending_received:
            sp = req.get("sender_profile", {})
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{sp.get('name', 'Unknown')}** wants to connect")
                if req.get("message"):
                    c1.caption(f'*"{req["message"]}"*')
                if c2.button("✅ Accept", key=f"acc_{req['id']}"):
                    r = api_patch(f"/connections/{req['id']}?action=accept", {})
                    if r:
                        st.success("Connection accepted!")
                        st.rerun()
                if c3.button("❌ Decline", key=f"dec_{req['id']}"):
                    r = api_patch(f"/connections/{req['id']}?action=decline", {})
                    if r:
                        st.rerun()
        st.divider()

    accepted = [r for r in received + sent if r.get("status") in ["accepted", "acceptd"]]
    if accepted:
        st.markdown("#### ✅ Connections")
        for req in accepted:
            if req["sender_id"] == st.session_state.user_id:
                partner = req.get("receiver_profile", {})
            else:
                partner = req.get("sender_profile", {})
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{partner.get('name', 'Unknown')}** — {partner.get('intent', '').title()}")
            c1.caption(partner.get("bio", "")[:100])
            if c2.button("💬", key=f"conn_msg_{req['id']}"):
                pid = req["receiver_id"] if req["sender_id"] == st.session_state.user_id else req["sender_id"]
                st.session_state.active_chat = pid
                st.session_state.page = "messages"
                st.rerun()
        st.divider()

    st.markdown("#### 📤 Sent Requests")
    if not sent:
        st.caption("No requests sent yet.")
    for req in sent:
        rp = req.get("receiver_profile", {})
        status_icon = {"pending": "⏳", "accepted": "✅", "acceptd": "✅", "declined": "❌", "declinesd": "❌"}.get(req["status"], "—")
        st.markdown(f"{status_icon} Request to **{rp.get('name', 'Unknown')}** — *{req['status'].title()}*")


# ──────────────────────────────────────────────
# PAGE: SETTINGS
# ──────────────────────────────────────────────
def page_settings():
    st.markdown("## Settings")
    profile = st.session_state.user_profile or {}

    st.markdown("#### Visibility")
    is_public = profile.get("is_public", True)
    new_public = st.toggle("Public Profile", value=is_public,
                           help="When off, other members won't see you in search or discovery.")
    if new_public != is_public:
        r = api_patch(f"/users/{st.session_state.user_id}", {"is_public": new_public})
        if r:
            refresh_profile()
            st.success(f"Profile is now {'public' if new_public else 'private'}.")

    st.divider()
    st.markdown("#### Block a User")
    users_data = api_get("/users", params={"requester_id": st.session_state.user_id})
    if users_data:
        other_users = {u["name"]: u["id"] for u in users_data.get("users", [])}
        if other_users:
            block_name = st.selectbox("Select user to block", list(other_users.keys()))
            if st.button("🚫 Block User", type="secondary"):
                r = api_post("/users/block", {
                    "blocker_id": st.session_state.user_id,
                    "blocked_id": other_users[block_name],
                })
                if r:
                    st.success(f"{block_name} has been blocked.")

    st.divider()
    st.markdown("#### Export Profile")
    if st.button("📥 Export My Profile as JSON"):
        st.download_button(
            "💾 Download profile.json",
            data=json.dumps(st.session_state.user_profile, indent=2),
            file_name="supernetwork_profile.json",
            mime="application/json",
        )


# ──────────────────────────────────────────────
# ROUTING
# ──────────────────────────────────────────────
page = st.session_state.page

if not st.session_state.user_id:
    if page == "register":
        page_register()
    elif page == "login":
        page_login()
    else:
        page_home()
else:
    if page == "profile":
        page_profile()
    elif page == "search":
        page_search()
    elif page == "discover":
        page_discover()
    elif page == "messages":
        page_messages()
    elif page == "connections":
        page_connections()
    elif page == "settings":
        page_settings()
    else:
        page_search()
