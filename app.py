import uuid
import os
import streamlit as st
from chains.rag_chain import create_rag_chain

SESSION_FILE = "session_id.txt"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎬 Movie Chatbot",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Movie Chatbot")
st.caption("Ask me anything about movies — Bollywood, Hollywood, or beyond!")

# ── Initialize everything ONCE using session_state ─────────────────────────────
if "initialized" not in st.session_state:

    # Load or create session ID
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            st.session_state.session_id = f.read().strip()
    else:
        st.session_state.session_id = str(uuid.uuid4())
        with open(SESSION_FILE, "w") as f:
            f.write(st.session_state.session_id)

    # Build chain ONCE — never rebuilt unless new session
    st.session_state.chain = create_rag_chain(st.session_state.session_id)

    # UI message history for displaying chat bubbles
    st.session_state.messages = []

    # ✅ Mark as initialized — this block never runs again until page refresh
    st.session_state.initialized = True

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("**Session ID:**")
    st.code(st.session_state.session_id, language=None)

    if st.button("🆕 New Session", use_container_width=True):
        new_id = str(uuid.uuid4())
        with open(SESSION_FILE, "w") as f:
            f.write(new_id)
        # ✅ Clear ALL session state and reinitialize
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.divider()
    st.markdown("**How to use:**")
    st.markdown("- Ask about any movie or show")
    st.markdown("- Ask follow-up questions naturally")
    st.markdown("- Click 'New Session' to clear history")

# ── Display existing chat history ──────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
if query := st.chat_input("Ask about a movie..."):

    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # ✅ Always use the same chain stored in session_state
                response = st.session_state.chain({"question": query})
                answer = response["answer"]
            except Exception as e:
                answer = f"⚠️ Something went wrong: {e}"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})