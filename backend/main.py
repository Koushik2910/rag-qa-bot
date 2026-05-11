from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from github_connector import fetch_repo_contents
from embedder import embed_documents, get_collection_stats, reset_collection
from chatbot import ask, find_coverage_gaps

app = FastAPI(title="RAG QA Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request Models ---
class RepoRequest(BaseModel):
    owner: str
    repo: str

class ChatRequest(BaseModel):
    question: str
    repo: str = None

class GapRequest(BaseModel):
    owner: str
    repo: str


# --- Routes ---
@app.get("/")
def root():
    return {"status": "RAG QA Bot is running"}


@app.post("/ingest")
def ingest_repo(request: RepoRequest):
    try:
        print(f"Fetching files from {request.owner}/{request.repo}...")
        documents = fetch_repo_contents(request.owner, request.repo)

        if not documents:
            raise HTTPException(
                status_code=404,
                detail="No supported files found in repo"
            )

        chunks_added = embed_documents(documents)
        stats = get_collection_stats()

        return {
            "status": "success",
            "repo": f"{request.owner}/{request.repo}",
            "files_fetched": len(documents),
            "chunks_added": chunks_added,
            "total_chunks_in_db": stats["total_chunks"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        result = ask(request.question, repo=request.repo)
        return {
            "status": "success",
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["sources"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gaps")
def coverage_gaps(request: GapRequest):
    try:
        result = find_coverage_gaps(request.owner, request.repo)
        return {
            "status": "success",
            "repo": request.repo,
            "analysis": result["analysis"],
            "sources": result["sources"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def stats():
    try:
        return get_collection_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reset")
def reset():
    try:
        reset_collection()
        return {"status": "success", "message": "Vector DB cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))