import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DB_PATH = "../chroma_db"
COLLECTION_NAME = "qa_knowledge"
GROQ_MODEL = "llama-3.3-70b-versatile"
CONFIDENCE_THRESHOLD = 0.7

SUPPORTED_EXTENSIONS = [".py", ".ts", ".java", ".js", ".md", ".txt"]