from dotenv import load_dotenv
load_dotenv()

import asyncio
import streamlit as st
import os

from agent import agent, Deps

st.set_page_config(
    page_title='DevPath',
    page_icon='📍',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    .stApp, .stApp > div { background-color: #0D1117 !important; }
    section[data-testid="stSidebar"] { background-color: #010409 !important; border-right: 1px solid #21262D; }
    p, label, span, .stMarkdown p { color: #C9D1D9 !important; }
    h1, h2, h3 { color: #F0F6FC !important; }
    a { color: #58A6FF !important; }
    hr { border-color: #21262D !important; }
    .stButton button { background-color: #161B22 !important; color: #C9D1D9 !important; border-color: #30363D !important; }
    .dp-title { font-size: 5rem !important; font-weight: 900 !important; letter-spacing: -0.04em; color: #F0F6FC !important; line-height: 1 !important; margin: 0 0 0.5rem 0 !important; }
    .dp-sub { font-size: 1.05rem; color: #8B949E !important; margin: 0 0 1rem 0; }
    .dp-badge { display: inline-flex; align-items: center; gap: 7px; background: #161B22; border: 1px solid #30363D; border-radius: 20px; padding: 5px 14px 5px 10px; font-size: 0.8rem; color: #8B949E !important; margin-bottom: 1rem; }
    .dp-dot { width: 8px; height: 8px; border-radius: 50%; background: #3FB950; flex-shrink: 0; }
    .ex-card { background: #161B22; border: 1px solid #21262D; border-radius: 10px; padding: 16px; font-size: 0.9rem; color: #8B949E !important; line-height: 1.5; }
    .src-label { font-size: 0.65rem !important; font-weight: 700 !important; letter-spacing: 0.1em; text-transform: uppercase; color: #484F58 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Your profile")
    st.caption("Fill in your details for more personalized answers")
    st.divider()
    skills_input = st.text_input("Current skills", placeholder="e.g. Python, SQL, Excel")
    target_role = st.selectbox("Target role", [
        "", "Data Engineer", "Data Scientist", "ML Engineer",
        "Backend Developer", "Frontend Developer", "Full-stack Developer",
        "DevOps Engineer", "Cloud Engineer", "Security Engineer", "Mobile Developer",
    ])
    region = st.text_input("Country or region", placeholder="e.g. Philippines, Germany")
    st.divider()
    st.markdown('<p class="src-label">Data sources</p>', unsafe_allow_html=True)
    st.markdown("[Stack Overflow Survey 2024](https://survey.stackoverflow.co/2024/)")
    st.markdown("[O\*NET 29.0 — US Dept of Labor](https://www.onetcenter.org/database.html)")
    st.markdown("[WEF Future of Jobs 2025](https://www.weforum.org/publications/the-future-of-jobs-report-2025/)")
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="dp-title">DevPath</p>', unsafe_allow_html=True)
st.markdown('<p class="dp-sub">Tech career planning grounded in real developer data from 65,000+ respondents across 185 countries</p>', unsafe_allow_html=True)
st.markdown('<div class="dp-badge"><span class="dp-dot"></span>Stack Overflow 2024 · O*NET 29.0 · WEF Future of Jobs 2025</div>', unsafe_allow_html=True)
st.divider()

# ── Chat ──────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="ex-card">How do I become a data engineer with Python and SQL?</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="ex-card">What skills are most in demand for ML engineers in 2024?</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="ex-card">Is data science a viable career in Southeast Asia?</div>', unsafe_allow_html=True)
    st.divider()

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            col1, col2, _ = st.columns([1, 1, 8])
            if col1.button("Helpful", key=f"up_{i}"):
                st.toast("Thanks for the feedback!")
            if col2.button("Not helpful", key=f"dn_{i}"):
                st.toast("Thanks, we will improve!")

if prompt := st.chat_input("Ask about your tech career..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.caption("Searching knowledge base...")
        try:
            deps = Deps(
                skills=[s.strip() for s in skills_input.split(",") if s.strip()],
                target_role=target_role,
                region=region
            )
            result = asyncio.run(agent.run(prompt, deps=deps))
            answer = result.output
        except Exception as e:
            answer = f"Error: {str(e)}"
        placeholder.empty()
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})