import uuid
import os
import streamlit as st
from chains.rag_chain import create_rag_chain 
import redis
from datetime import datetime
import json 

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

SESSION_FILE = "session_id.txt"


st.set_page_config(
    page_title="🎬 Movie Chatbot",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Movie Chatbot")
st.caption("Ask me anything about movies — Bollywood, Hollywood, or beyond!")

def add_session(session_id: str) -> None:
    redis_client.rpush("sessions", session_id)
    redis_client.hset(f"session_meta:{session_id}", mapping={
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "label": "Session",
    })

def get_sessions() -> list[str]:
    return redis_client.lrange("sessions", 0, -1)

def get_session_meta(session_id: str) -> dict:
    return redis_client.hgetall(f"session_meta:{session_id}")

def set_label(session_id: str, first_message: str) -> None:
    label = first_message[:35] + ("..." if len(first_message) > 35 else "")
    redis_client.hset(f"session_meta:{session_id}", "label", label)


def switch_session(session_id: str) -> None:
    st.session_state.session_id = session_id
    st.session_state.chain = create_rag_chain(session_id)

    try:
        saved = redis_client.lrange(f"messages:{session_id}", 0, -1)
        st.session_state.messages = [json.loads(m) for m in saved] if saved else []
    except Exception:
        st.session_state.messages = []

    st.session_state.initialized = True
    st.rerun()



if "initialized" not in st.session_state:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_id = f.read().strip()
    else:
        session_id = str(uuid.uuid4())
        with open(SESSION_FILE, "w") as f:
            f.write(session_id)

    # Register in Redis if not already present
    if session_id not in get_sessions():
        add_session(session_id)

    switch_session(session_id)   






with st.sidebar:
    st.header("🎬 Movie Chatbot")

    if st.button("➕ New Session", use_container_width=True):
        new_id = str(uuid.uuid4())
        add_session(new_id)
        switch_session(new_id)

    st.divider()
    st.subheader("🕘 Past Sessions")

    sessions = get_sessions()

    if not sessions:
        st.caption("No past sessions yet.")
    else:
        for sid in reversed(sessions):
            meta = get_session_meta(sid)

            st.markdown(meta.get("label", "Untitled Session"))

            if st.button("Load", key=sid):
                switch_session(sid)

            st.divider()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask about a movie..."):
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    if len(st.session_state.messages) == 1:
        set_label(st.session_state.session_id, query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chain({"question": query})
                answer = response.get("answer", "⚠️ No answer returned.")
            except Exception as e:
                answer = f"⚠️ Something went wrong: {e}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

   
    redis_client.rpush(f"messages:{st.session_state.session_id}", 
                       json.dumps({"role": "user", "content": query}))
    redis_client.rpush(f"messages:{st.session_state.session_id}", 
                       json.dumps({"role": "assistant", "content": answer}))