from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_retriever():

# Embedding model (converts text → vectors)
 embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load existing Chroma vector database
 vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# Create retriever from vector database
 retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}  # retrieve top 5 relevant movie documents
)

 return retriever