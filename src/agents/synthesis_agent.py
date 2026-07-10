"""
Step 5: Synthesis Agent.

Reviews the complete debate transcript across all agents and rounds, and
produces a single structured risk-assessment report.
"""
from __future__ import annotations

import json
from typing import Any

from src.llm.groq_client import generate

SYSTEM_PROMPT = (
    "You are the Synthesis Agent chairing an institutional investment "
    "committee. You have listened to the full debate between the Bull, Bear, "
    "and Macro Risk agents. Your job is to weigh their arguments objectively "
    "and produce a structured, balanced risk assessment. You do not introduce "
    "new claims not grounded in the debate or the underlying data. "
    "The debate transcript contains citation tags like [pe_ratio] after "
    "claims that reference specific data points — carry the relevant tags "
    "into your own strengths/weaknesses/investment_outlook text so the "
    "report stays traceable back to the underlying data. Never invent a "
    "citation id that didn't appear in the transcript. "
    "Respond ONLY with valid JSON — no markdown fences, no commentary."
)

REPORT_SCHEMA_HINT = """
Respond with a JSON object matching exactly this shape:
{
  "ticker": string,
  "overall_risk_level": "Low" | "Medium" | "High",
  "strengths": [string, ...],
  "weaknesses": [string, ...],
  "investment_outlook": string,
  "confidence_score": number  // 0-100
}
""".strip()


def _format_transcript(transcript: list[dict[str, str]]) -> str:
    return "\n".join(f"{turn['role']}: {turn['content']}" for turn in transcript)


def synthesize(market_data: dict[str, Any], transcript: list[dict[str, str]]) -> dict[str, Any]:
    """
    Step 6 input generator: produce the final structured report dict that
    the Streamlit dashboard renders.
    """
    user_prompt = f"""
Ticker under review: {market_data.get('ticker')} ({market_data.get('company_name')})

Full debate transcript:
{_format_transcript(transcript)}

{REPORT_SCHEMA_HINT}
""".strip()

    raw = generate(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt, temperature=0.2)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: LLM occasionally wraps JSON in prose/fences despite instructions.
        cleaned = raw.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "ticker": market_data.get("ticker"),
                "overall_risk_level": "Unknown",
                "strengths": [],
                "weaknesses": [],
                "investment_outlook": raw,
                "confidence_score": None,
                "parse_error": True,
            }
