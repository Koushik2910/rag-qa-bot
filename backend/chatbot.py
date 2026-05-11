from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from retriever import get_context_for_query, get_sources_for_query

client = Groq(api_key=GROQ_API_KEY)


def ask(question: str) -> dict:
    context = get_context_for_query(question)
    sources = get_sources_for_query(question)

    prompt = f"""You are a QA Knowledge Assistant. Answer questions about test files.

Context from test files:
{context}

Question: {question}

Rules:
- Answer in maximum 5 bullet points
- Mention specific file names and function names
- If not found in context, say "Not found in indexed files"
- Do NOT repeat yourself

Answer:"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500,
        stop=None
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "sources": sources,
        "question": question
    }


def find_coverage_gaps(owner: str, repo: str) -> dict:
    gap_prompt = f"""Based on the test files from the repository {owner}/{repo}, 
analyze what is being tested and identify gaps.

Look at the test files in context and:
1. List what features/flows ARE currently tested
2. List what common features are likely MISSING from tests
3. Suggest 5 specific test cases that should be added

Be specific about file names and function names you see.

Context will be provided by the system."""

    context = get_context_for_query(
        f"test coverage features tested in {repo}"
    )

    full_prompt = f"""You are a QA Coverage Analyst. Analyze these test files and 
find coverage gaps.

Test files context:
{context}

{gap_prompt}

Format your response as:
COVERED:
- list what is tested

GAPS FOUND:
- list what is missing

SUGGESTED TEST CASES:
- specific test cases to add"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.2,
        max_tokens=1500
    )

    answer = response.choices[0].message.content.strip()

    return {
        "analysis": answer,
        "repo": repo,
        "sources": sources_for_gap(owner, repo)
    }


def sources_for_gap(owner: str, repo: str) -> list:
    return get_sources_for_query(f"test coverage {repo}")