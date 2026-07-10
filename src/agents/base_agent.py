"""
Shared behavior for all debate agents (Bull, Bear, Macro).

Each concrete agent supplies a role name, a persona/system prompt, and a
perspective description. The base class handles building the prompt from
market data + prior debate transcript and calling the LLM.
"""
from __future__ import annotations

from typing import Any

from src.llm.groq_client import generate


class BaseAgent:
    role: str = "Agent"
    persona: str = "You are a financial analyst."

    def _format_market_data(self, market_data: dict[str, Any]) -> str:
        hist = market_data.get("historical_performance") or {}
        news = market_data.get("recent_news") or []
        news_lines = "\n".join(
            f"- [news_{i}] {n.get('headline')}" for i, n in enumerate(news)
        ) or "- No recent news available."

        return f"""
Ticker: {market_data.get('ticker')}
Company: {market_data.get('company_name')}
Current Price [current_price]: {market_data.get('current_price')}
Market Cap [market_cap]: {market_data.get('market_cap')}
P/E Ratio [pe_ratio]: {market_data.get('pe_ratio')}
Forward P/E [forward_pe]: {market_data.get('forward_pe')}
Revenue Growth [revenue_growth]: {market_data.get('revenue_growth')}
Profit Margins [profit_margins]: {market_data.get('profit_margins')}
Debt to Equity [debt_to_equity]: {market_data.get('debt_to_equity')}
Sector [sector]: {market_data.get('sector')}
Industry [industry]: {market_data.get('industry')}
52-Week High/Low [fifty_two_week_high] / [fifty_two_week_low]: {market_data.get('fifty_two_week_high')} / {market_data.get('fifty_two_week_low')}
6-Month Performance [historical_performance]: {hist}

Recent News:
{news_lines}
""".strip()

    def _format_transcript(self, transcript: list[dict[str, str]]) -> str:
        if not transcript:
            return "No prior arguments yet — you are opening the debate."
        lines = [f"{turn['role']}: {turn['content']}" for turn in transcript]
        return "\n".join(lines)

    def analyze(self, market_data: dict[str, Any], transcript: list[dict[str, str]]) -> str:
        """
        Generate this agent's argument given the market data and the debate
        so far. Concrete subclasses just set `role` and `persona`.
        """
        data_block = self._format_market_data(market_data)
        transcript_block = self._format_transcript(transcript)

        user_prompt = f"""
Here is the financial data for {market_data.get('ticker')}. Each data point
has a citation id in square brackets, e.g. [pe_ratio].

{data_block}

Debate so far:
{transcript_block}

As the {self.role}, respond with your argument in 3-5 concise sentences.
If prior arguments exist, directly challenge or refine your position in light
of them. Stay strictly within your assigned perspective.

CITATION RULES:
- Whenever you state a claim that relies on a specific data point above,
  append that data point's citation id in square brackets right after the
  claim, e.g. "The stretched valuation [pe_ratio] is a concern."
- Only use ids that appear in the data block above — never invent new ids.
- Not every sentence needs a citation (e.g. framing/transition sentences),
  but any sentence citing a number, headline, or fact must include one.
""".strip()

        return generate(system_prompt=self.persona, user_prompt=user_prompt)