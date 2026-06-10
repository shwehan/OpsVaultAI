import os

from groq import Groq

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the provided "
    "knowledge base context. If the context does not contain enough information "
    "to answer confidently, say so explicitly. Always cite the source document "
    "for each claim."
)

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in environment")
        _client = Groq(api_key=api_key)
    return _client


def generate_answer(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{c['source_id']}]\n{c['snippet']}" for c in chunks
    )
    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    response = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content
