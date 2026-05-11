from importlib.metadata import files

import requests
from config import GITHUB_TOKEN

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

SUPPORTED_EXTENSIONS = [".py", ".ts", ".java", ".js", ".md", ".txt"]
EXCLUDED_FILES = [".env", ".env.example", "healing_log.json", "test_results.txt"]

def get_repo_files(owner: str, repo: str) -> list:
    files = []
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching repo: {response.status_code}")
        return files

    tree = response.json().get("tree", [])

    for item in tree:
        path = item.get("path", "")
        if item.get("type") == "blob":
            ext = "." + path.split(".")[-1] if "." in path else ""
            filename = path.split("/")[-1]
            if ext in SUPPORTED_EXTENSIONS and filename not in EXCLUDED_FILES:
                files.append({
                    "path": path,
                    "url": item.get("url"),
                    "repo": repo,
                    "owner": owner
                })

    print(f"Found {len(files)} files in {owner}/{repo}")
    return files


def get_file_content(file_info: dict) -> str:
    import base64
    response = requests.get(file_info["url"], headers=headers)

    if response.status_code != 200:
        return ""

    content = response.json().get("content", "")
    encoding = response.json().get("encoding", "")

    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="ignore")

    return content


def fetch_repo_contents(owner: str, repo: str) -> list:
    documents = []
    files = get_repo_files(owner, repo)

    for file_info in files:
        content = get_file_content(file_info)
        if content.strip():
            documents.append({
                "content": content,
                "metadata": {
                    "source": file_info["path"],
                    "repo": repo,
                    "owner": owner,
                    "type": "github"
                }
            })

    print(f"Fetched {len(documents)} files with content from {owner}/{repo}")
    return documents
