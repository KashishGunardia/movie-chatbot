# 🎬 Movie Chatbot

A conversational AI chatbot that answers questions about movies using RAG (Retrieval-Augmented Generation). It remembers your entire conversation history and can answer follow-up questions naturally.

## Features

- 🔍 Searches a real movie database for accurate information
- 🧠 Remembers full conversation history using Redis
- 💬 Handles follow-up questions naturally
- 🌐 Clean chat UI built with Streamlit
- 📝 Summarizes old conversations so nothing is ever forgotten

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.1 8B via Groq API |
| Vector Database | Chroma |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Memory | Redis + ConversationSummaryBufferMemory |
| Framework | LangChain |
| UI | Streamlit |

## Project Structure

```
movie chatbot/
│
├── app.py                    ← Streamlit UI entry point
├── requirements.txt          ← Python dependencies
├── .env.example              ← Environment variables template
│
├── chains/
│   └── rag_chain.py          ← RAG pipeline (condense → retrieve → answer)
│
├── memory/
│   └── redis_memory.py       ← Persistent chat history in Redis
│
├── retriever/
│   └── movie_retriever.py    ← Chroma vector search
│
└── ingest.py                 ← Builds vector DB from movie CSV
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/movie-chatbot.git
cd movie-chatbot
```

### 2. Create conda environment
```bash
conda create -n moviebot python=3.10
conda activate moviebot
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```
Fill in your actual values in `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
REDIS_URL=redis://localhost:6379
```

### 4. Install and start Redis
Download Redis for Windows from:
`https://github.com/microsoftarchive/redis/releases`

Then run as a Windows service:
```cmd
.\redis-server.exe --service-install redis.windows-service.conf
.\redis-server.exe --service-start
```

### 5. Add your movie dataset
Place your `imdb-movies-dataset.csv` in the project folder and run:
```bash
python ingest.py
```
This builds the `vector_db/` folder.

### 6. Run the chatbot
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

## How It Works

```
You type a question
        ↓
Step 1 — CONDENSE: LLM rewrites follow-up into standalone question using chat history
        ↓
Step 2 — RETRIEVE: Chroma finds top 5 relevant movie documents
        ↓
Step 3 — ANSWER: LLM generates response using history + retrieved docs
        ↓
Step 4 — SAVE: Question + answer saved to Redis for future turns
```

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com |
| `REDIS_URL` | Redis connection string (default: `redis://localhost:6379`) |