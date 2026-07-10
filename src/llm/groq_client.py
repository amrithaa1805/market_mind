"""
Thin wrapper around the Groq API so agents don't each re-implement
client setup, retries, and error handling.
"""
from __future__ import annotations

from groq import Groq

from src.config import settings

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file before running MarketMind."
            )
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def generate(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    """
    Send a single chat completion request to Groq and return the text response.
    """
    client = get_client()
    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return completion.choices[0].message.content.strip()
