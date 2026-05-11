from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from retriever import get_context_for_query, get_sources_for_query

client = Groq(api_key=GROQ_API_KEY)


def ask(question: str, repo: str = None) -> dict:
    context = get_context_for_query(question, repo=repo)
    sources = get_sources_for_query(question, repo=repo)

    prompt = f"""You are a QA Knowledge Assistant helping engineers understand test coverage.

Context from repository files (use this to understand the codebase, do NOT reproduce the code in your answer):
{context}

Question: {question}

Rules:
- Answer in maximum 5 bullet points
- A TEST file starts with test_ or ends with _test — functions in these files are actual tests
- Source code files (main.py, healer.py, chatbot.py etc) are NOT tests
- If you see no test_ files in context, say "No test files found in this repo"
- Mention specific file names and function names when relevant
- Do NOT repeat yourself

Answer:"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )

    answer = response.choices[0].message.content.strip()
    return {
        "answer": answer,
        "sources": sources,
        "question": question
    }


def find_coverage_gaps(owner: str, repo: str) -> dict:
    context = get_context_for_query(
        f"test coverage features tested in {repo}", repo=repo
    )

    prompt = f"""You are a QA Coverage Analyst for the repository: {repo}

Context from repository files:
{context}

Analyze the files and answer:
1. What is ACTUALLY tested — only count files starting with test_ or ending with _test
2. What SOURCE CODE files exist but have NO corresponding test files
3. Suggest 5 specific test cases to add

Important:
- Do NOT treat source code functions as tests
- If no test_ files exist, say the repo has zero test coverage
- Be specific about file names

Format exactly as:
COVERED:
- list only real test functions found

GAPS FOUND:
- list source files with no tests

SUGGESTED TEST CASES:
1. specific test case
2. specific test case
3. specific test case
4. specific test case
5. specific test case"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000
    )

    answer = response.choices[0].message.content.strip()
    return {
        "analysis": answer,
        "repo": repo,
        "sources": get_sources_for_query(f"test coverage {repo}", repo=repo)
    }