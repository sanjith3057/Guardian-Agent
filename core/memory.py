"""
Chroma DB memory implementation for GUARDIAN-AGENT.
Provides vector-based long-term storage for research and observations.
"""
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv(override=True)

# Load Chroma DB config from .env
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")

def get_memory_client():
    """
    Initializes and returns a Chroma DB client.
    """
    return chromadb.HttpClient(
        host="api.trychroma.com", # Update if using a different host
        headers={"Authorization": f"Bearer {CHROMA_API_KEY}"},
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE
    )

def save_to_memory(collection_name: str, doc_id: str, document: str, metadata: dict = None):
    """
    Saves a document to the specified Chroma collection.
    """
    try:
        client = get_memory_client()
        collection = client.get_or_create_collection(name=collection_name)
        collection.add(
            documents=[document],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        print(f"✅ MEMORY: Saved to {collection_name}")
    except Exception as e:
        print(f"⚠️ MEMORY ERROR: {e}")

def query_memory(collection_name: str, query: str, n_results: int = 3):
    """
    Queries the specified Chroma collection.
    """
    try:
        client = get_memory_client()
        collection = client.get_collection(name=collection_name)
        return collection.query(
            query_texts=[query],
            n_results=n_results
        )
    except Exception as e:
        print(f"⚠️ MEMORY QUERY ERROR: {e}")
        return None
