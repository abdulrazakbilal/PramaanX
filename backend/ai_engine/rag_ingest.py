# backend/ai_engine/rag_ingest.py
import os
import chromadb
from chromadb.utils import embedding_functions
# Let's stick to the libraries you have. We will use a simple text extraction helper.

# UPDATE: Let's add 'pypdf' to your environment for reading PDFs easily.
# Run this in terminal now: pip install pypdf

from pypdf import PdfReader

# 1. Setup ChromaDB
DB_PATH = os.path.join(os.getcwd(), "backend", "data", "chroma_db")
client = chromadb.PersistentClient(path=DB_PATH)

# Use a free, local embedding model (runs on your CPU)
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2" 
)

# Create or get the collection
collection = client.get_or_create_collection(
    name="government_rules",
    embedding_function=embed_fn
)

def ingest_data():
    pdf_path = os.path.join(os.getcwd(), "backend", "data", "rules_pdfs", "ap_rto_fees.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at {pdf_path}")
        return

    print("📖 Reading PDF...")
    reader = PdfReader(pdf_path)
    text_content = ""
    for page in reader.pages:
        text_content += page.extract_text() + "\n"

    # Simple chunking (splitting text into smaller pieces)
    chunks = []
    chunk_size = 300 # characters
    for i in range(0, len(text_content), chunk_size):
        chunks.append(text_content[i:i+chunk_size])

    print(f"🧩 Split into {len(chunks)} chunks. Storing in ChromaDB...")

    # Add to Database
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"source": "ap_rto_fees.pdf"} for _ in range(len(chunks))]
    )
    
    print("✅ Data Ingested Successfully! The AI now knows the rules.")

if __name__ == "__main__":
    ingest_data()