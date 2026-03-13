import os
from dotenv import load_dotenv
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_groq import ChatGroq

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")


def get_memory(session_id: str):

    chat_history = RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=60 * 60 * 24 * 7  # 7 days
    )

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    memory = ConversationSummaryBufferMemory(
        llm=llm,
        chat_memory=chat_history,
        max_token_limit=2000,
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        return_messages=False  # plain text string — we handle it ourselves now
    )

    return memory