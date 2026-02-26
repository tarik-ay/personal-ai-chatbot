import anthropic
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

PROFILE_PATH = "tarik_profile.md"

SUGGESTED_QUESTIONS = [
    "What is Tarik's current role and focus?",
    "Which industries has Tarik worked in?",
    "What are Tarik's key skills?",
    "What is Tarik's product philosophy?",
    "What was Tarik's biggest project impact?",
    "What kind of roles is Tarik looking for?",
]

SYSTEM_PROMPT = """\
You are a professional personal assistant that answers questions about Tarik \
based solely on the profile provided below.
If the answer is not found in the profile, respond with exactly: \
"That's not covered in Tarik's profile."
Do not use any outside knowledge. Be concise, professional, and friendly.

--- TARIK'S PROFILE ---
{profile}
--- END OF PROFILE ---"""

# JS injected inside an iframe (via components.html) that reaches into the
# parent Streamlit page and forces all 6 suggestion buttons to the same height.
_EQUALIZE_JS = """
<script>
function equalize() {
    try {
        var sel = '[data-testid="column"] button, [data-testid="stColumn"] button';
        var btns = Array.from(parent.document.querySelectorAll(sel));
        if (!btns.length) return;
        btns.forEach(function(b) { b.style.height = 'auto'; });
        var maxH = btns.reduce(function(m, b) {
            return Math.max(m, b.getBoundingClientRect().height);
        }, 0);
        if (maxH > 0) {
            btns.forEach(function(b) {
                b.style.setProperty('height', maxH + 'px', 'important');
                b.style.setProperty('min-height', maxH + 'px', 'important');
            });
        }
    } catch(e) {}
}
[50, 200, 500, 1000].forEach(function(t) { setTimeout(equalize, t); });
</script>
"""


def log_question(question: str) -> None:
    with open("chat_logs.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {question}\n")


@st.cache_data
def load_profile(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def get_response(client: anthropic.Anthropic, system: str, history: list, question: str) -> str:
    messages = history + [{"role": "user", "content": question}]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def main():
    st.set_page_config(
        page_title="Tarik · Personal Chatbot",
        page_icon="💼",
        layout="centered",
    )

    st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Profile header */
    .profile-card {
        background: linear-gradient(135deg, #0f2044 0%, #1a3a6b 60%, #1e4d8c 100%);
        border-radius: 14px;
        padding: 28px 32px;
        display: flex;
        align-items: center;
        gap: 22px;
        margin-bottom: 8px;
        box-shadow: 0 4px 20px rgba(15,32,68,0.25);
    }
    .avatar-circle {
        width: 68px;
        height: 68px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 800;
        color: white;
        flex-shrink: 0;
        border: 3px solid rgba(255,255,255,0.2);
    }
    .profile-name  { font-size: 28px; font-weight: 700; color: #ffffff; margin: 0 0 6px 0; letter-spacing: -0.3px; }
    .profile-title { font-size: 14px; color: #93c5fd; margin: 0 0 4px 0; font-weight: 500; }
    .profile-meta  { font-size: 13px; color: rgba(255,255,255,0.5); margin: 0; }

    /* Section label */
    .section-label {
        font-size: 11px; font-weight: 700; color: #64748b;
        text-transform: uppercase; letter-spacing: 1px; margin: 20px 0 10px 2px;
    }

    /* Suggestion buttons — styling only, height is set by JS */
    div[data-testid="column"] .stButton > button,
    div[data-testid="stColumn"] .stButton > button {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #374151 !important;
        border-radius: 10px !important;
        padding: 11px 14px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.45 !important;
        width: 100% !important;
        transition: border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
        overflow: hidden !important;
    }
    div[data-testid="column"] .stButton > button:hover,
    div[data-testid="stColumn"] .stButton > button:hover {
        border-color: #3b82f6 !important;
        color: #1d4ed8 !important;
        background: #eff6ff !important;
        box-shadow: 0 3px 10px rgba(59,130,246,0.18) !important;
    }

    /* Chat input */
    .stChatInput textarea { border-radius: 10px !important; font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Load profile & init client ────────────────────────────────────────────
    profile = load_profile(PROFILE_PATH)
    system_prompt = SYSTEM_PROMPT.format(profile=profile)
    client = anthropic.Anthropic()

    # ── Session state ─────────────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # ── Process pending suggestion ────────────────────────────────────────────
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        log_question(question)
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Thinking…"):
            answer = get_response(client, system_prompt, st.session_state.messages[:-1], question)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # ── Profile header ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="profile-card">
        <div class="avatar-circle">T</div>
        <div>
            <div class="profile-name">Tarik</div>
            <div class="profile-title">Product Manager · Liquidity Capital</div>
            <div class="profile-meta">Abu Dhabi &nbsp;·&nbsp; Fintech · Loyalty · AI Products</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Suggested questions ───────────────────────────────────────────────────
    st.markdown('<div class="section-label">Suggested questions</div>', unsafe_allow_html=True)

    row1 = st.columns(3)
    row2 = st.columns(3)
    grid = row1 + row2
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        with grid[i]:
            if st.button(question, key=f"sq_{i}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()

    # Inject JS to measure and equalize all suggestion button heights
    components.html(_EQUALIZE_JS, height=0)

    # ── Chat area ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Chat</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "Hi! I'm Tarik's personal assistant. Ask me anything about his "
                "experience, skills, or background — I'll answer based on his profile."
            )

    # ── Chat input ────────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask anything about Tarik…"):
        log_question(prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer = get_response(client, system_prompt, st.session_state.messages, prompt)
            st.markdown(answer)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
