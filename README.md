# QA Coverage Agent — AI-Powered Test Knowledge Bot

> Ask questions about your live GitHub test repos using RAG + Groq + ChromaDB

## What It Does
- Connects to your **live GitHub repos** — no manual uploads
- Answers questions like *"What tests cover login?"* from your actual code
- Finds **coverage gaps** automatically — tells you what's NOT tested
- Suggests specific test cases to fill the gaps
- Shows exact **source file + relevance score** for every answer

## Tech Stack
| Layer | Tool |
|---|---|
| LLM | Groq — Llama 3.3 70B (free) |
| Embeddings | sentence-transformers — all-MiniLM-L6-v2 (free, local) |
| Vector DB | ChromaDB (free, local, persistent) |
| Backend | Python FastAPI |
| Frontend | React + Vite |
| Source | GitHub API (live repo reading) |

## How It Works
```
GitHub Repo → FastAPI → sentence-transformers → ChromaDB
                                                     ↓
React UI ← FastAPI ← Groq LLM ← relevant chunks ←──┘
```

## Project Structure
```
rag-qa-bot/
├── backend/
│   ├── main.py              # FastAPI routes
│   ├── github_connector.py  # Fetches live GitHub files
│   ├── embedder.py          # Chunks + embeds into ChromaDB
│   ├── retriever.py         # Searches ChromaDB
│   ├── chatbot.py           # Groq LLM answer generation
│   └── config.py            # Settings
├── frontend/
│   └── src/App.jsx          # React chat UI
└── chroma_db/               # Auto-created vector store
```

## Setup

### Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn python-dotenv groq chromadb sentence-transformers PyPDF2 python-docx requests
```

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token
```

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## Usage
1. Enter your GitHub username and repo name in the sidebar
2. Click **Index Repo** — AI reads and indexes your test files
3. Ask questions in the chat:
   - *"What tests do we have?"*
   - *"How does the login test work?"*
   - *"What is not covered?"*
4. Click **Find Coverage Gaps** for automatic gap analysis

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | /ingest | Index a GitHub repo |
| POST | /chat | Ask a question |
| POST | /gaps | Find coverage gaps |
| GET | /stats | ChromaDB stats |
| DELETE | /reset | Clear vector DB |

## Author
**Koushik** — Senior QA Engineer
- GitHub: [Koushik2910](https://github.com/Koushik2910)
- LinkedIn: [linkedin.com/in/saikoushikgattu](https://www.linkedin.com/in/saikoushikgattu)
