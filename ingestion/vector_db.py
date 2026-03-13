import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

print("Loading dataset...")

df = pd.read_csv(r"C:/Users/LENOVO/Downloads/movie data/imdb-movies-dataset.csv")

print("Rows:", len(df))

documents = []

for _, row in df.iterrows():

    text = f"""
    Title: {row['Title']}
    Year: {row['Year']}
    Genre: {row['Genre']}
    Director: {row['Director']}
    Cast: {row['Cast']}
    Duration: {row['Duration (min)']} minutes
    Rating: {row['Rating']}
    Description: {row['Description']}
    """

    doc = Document(
        page_content=text,
        metadata={
            "title": row["Title"],
            "genre": row["Genre"],
            "year": row["Year"],
            "rating": row["Rating"]
        }
    )

    documents.append(doc)

print("Total documents:", len(documents))

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Creating vector database...")

vectorstore = Chroma.from_documents(
    documents,
    embedding=embeddings,
    persist_directory="vector_db"
)

vectorstore.persist()

print("Vector DB created successfully")