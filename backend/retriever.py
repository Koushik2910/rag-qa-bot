from sentence_transformers import SentenceTransformer
import chromadb
from config import EMBEDDING_MODEL, CHROMA_DB_PATH, COLLECTION_NAME

model = SentenceTransformer(EMBEDDING_MODEL)
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def search(query: str, n_results: int = 5, repo: str = None) -> list:
    query_embedding = model.encode(query).tolist()

    where_filter = {"repo": {"$eq": repo}} if repo else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        formatted.append({
            "content": doc,
            "source": meta.get("source", "unknown"),
            "repo": meta.get("repo", "unknown"),
            "owner": meta.get("owner", "unknown"),
            "score": round(1 - dist, 3)
        })

    return formatted


def get_context_for_query(query: str, repo: str = None) -> str:
    results = search(query, repo=repo)

    if not results:
        return "No relevant context found."

    context_parts = []
    for i, result in enumerate(results):
        context_parts.append(
            f"--- Source {i+1}: {result['repo']}/{result['source']} "
            f"(relevance: {result['score']}) ---\n{result['content']}"
        )

    return "\n\n".join(context_parts)


def get_sources_for_query(query: str, repo: str = None) -> list:
    results = search(query, repo=repo)
    seen = set()
    sources = []

    for result in results:
        key = f"{result['repo']}/{result['source']}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "file": result["source"],
                "repo": result["repo"],
                "score": result["score"]
            })

    return sources