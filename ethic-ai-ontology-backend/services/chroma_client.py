import os

import chromadb


def get_chroma_client():
    return chromadb.PersistentClient(
        path=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    )


def get_or_create_collection(name: str = "legal_documents"):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
