import chromadb
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, CHROMA_DB_PATH, COLLECTION_NAME

model = SentenceTransformer(EMBEDDING_MODEL)
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def embed_documents(documents: list) -> int:
    total_chunks = 0

    for doc in documents:
        content = doc["content"]
        metadata = doc["metadata"]
        source = metadata["source"]

        chunks = chunk_text(content)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{metadata['repo']}_{source}_{i}".replace("/", "_")

            existing = collection.get(ids=[chunk_id])
            if existing["ids"]:
                continue

            embedding = model.encode(chunk).tolist()

            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": source,
                    "repo": metadata["repo"],
                    "owner": metadata["owner"],
                    "chunk_index": i,
                    "type": metadata["type"]
                }]
            )
            total_chunks += 1

    print(f"Embedded {total_chunks} new chunks into ChromaDB")
    return total_chunks


def get_collection_stats() -> dict:
    count = collection.count()
    return {
        "total_chunks": count,
        "collection_name": COLLECTION_NAME
    }


def reset_collection():
    client.delete_collection(name=COLLECTION_NAME)
    global collection
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    print("Collection reset successfully")
