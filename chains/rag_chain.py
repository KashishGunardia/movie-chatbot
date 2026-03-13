from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from retriever.movie_retriever import get_retriever
from memory.redis_memory import get_memory


def format_docs(docs):
    if not docs:
        return "No specific movie records found."
    return "\n\n".join([doc.page_content for doc in docs])


def create_rag_chain(session_id):

    retriever = get_retriever()
    memory = get_memory(session_id)

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.5
    )

    condense_prompt = PromptTemplate.from_template(
        "Given the conversation history and a follow-up question, "
        "rephrase the follow-up into a standalone question with full context. "
        "If it's already standalone, return it as-is.\n\n"
        "Chat History:\n{chat_history}\n\n"
        "Follow-up: {question}\n\n"
        "Standalone question:"
    )

    qa_prompt = PromptTemplate.from_template(
        """You are a friendly and knowledgeable movie assistant.

RULES:
- Answer directly and confidently using your own knowledge
- NEVER say "I don't have context" or "no information found"  
- NEVER mention the database, retrieved records, or context to the user
- NEVER ask the user to re-provide information
- For follow-up questions like "which one should I watch?" or "who directed it?"
  ALWAYS refer back to the movies mentioned in the Chat History below
- For short replies like "okay", "cool", "thanks" respond naturally and briefly
- For ratings always use IMDB score out of 10
- Keep responses concise and conversational

--- Chat History (use this to answer follow-up questions) ---
{chat_history}

--- Retrieved Movie Records ---
{context}

Question: {question}

Answer:"""
    )

    def run_chain(inputs):
        question = inputs["question"]

        # Load full history from Redis
        memory_vars = memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", "")

        # Step 1: Condense follow-up into standalone question
        standalone = (condense_prompt | llm | StrOutputParser()).invoke({
            "chat_history": chat_history,
            "question": question
        })

        # Step 2: Retrieve relevant docs using standalone question
        docs = retriever.invoke(standalone)
        context = format_docs(docs)

        # Step 3: Generate answer — pass chat_history directly into QA prompt
        answer = (qa_prompt | llm | StrOutputParser()).invoke({
            "chat_history": chat_history,  # ✅ history now in QA prompt too
            "context": context,
            "question": standalone
        })

        # Step 4: Save to Redis
        memory.save_context({"question": question}, {"answer": answer})

        return {"answer": answer, "source_documents": docs}

    return run_chain