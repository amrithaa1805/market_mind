"""
Explainability / citation layer.

Every fact the agents are given (P/E ratio, market cap, a specific news
headline, etc.) gets a short, stable ID AND a real source URL. Agents are
instructed to tag their claims with these IDs inline, e.g.:

    "The stretched valuation [pe_ratio] combined with slowing growth
    [revenue_growth] raises concern."

This module builds that ID -> {label, value, url} registry from market_data,
and renders any [id] tags found in agent text into small hoverable footnote
markers that link out to the real page the number came from — Yahoo Finance
for fundamentals (since that's what yfinance itself scrapes), and the actual
article URL for news items — so a user can independently verify every claim.
"""
from __future__ import annotations

import re
from typing import Any

_CITATION_PATTERN = re.compile(r"\[([a-zA-Z0-9_]+)\]")


def build_citation_registry(market_data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """
    Maps a short citation id -> {"label": human-readable name, "value": the
    actual data point, "url": a real, clickable page the value can be
    verified against}. IDs here must match what _format_market_data() in
    base_agent.py shows the LLM, since the LLM is what generates the tags.
    """
    ticker = market_data.get("ticker", "")
    hist = market_data.get("historical_performance") or {}

    # yfinance itself sources its data from Yahoo Finance, so these pages
    # are the actual origin of every fundamental number below — not just a
    # generic search link.
    quote_url = f"https://finance.yahoo.com/quote/{ticker}"
    stats_url = f"{quote_url}/key-statistics"
    profile_url = f"{quote_url}/profile"
    history_url = f"{quote_url}/history"
    financials_url = f"{quote_url}/financials"

    registry: dict[str, dict[str, str]] = {
        "current_price": {
            "label": "Current Price", "value": str(market_data.get("current_price")), "url": quote_url,
        },
        "market_cap": {
            "label": "Market Cap", "value": str(market_data.get("market_cap")), "url": stats_url,
        },
        "pe_ratio": {
            "label": "P/E Ratio (trailing)", "value": str(market_data.get("pe_ratio")), "url": stats_url,
        },
        "forward_pe": {
            "label": "Forward P/E", "value": str(market_data.get("forward_pe")), "url": stats_url,
        },
        "revenue_growth": {
            "label": "Revenue Growth", "value": str(market_data.get("revenue_growth")), "url": financials_url,
        },
        "profit_margins": {
            "label": "Profit Margins", "value": str(market_data.get("profit_margins")), "url": stats_url,
        },
        "debt_to_equity": {
            "label": "Debt to Equity", "value": str(market_data.get("debt_to_equity")), "url": stats_url,
        },
        "sector": {
            "label": "Sector", "value": str(market_data.get("sector")), "url": profile_url,
        },
        "industry": {
            "label": "Industry", "value": str(market_data.get("industry")), "url": profile_url,
        },
        "fifty_two_week_high": {
            "label": "52-Week High", "value": str(market_data.get("fifty_two_week_high")), "url": quote_url,
        },
        "fifty_two_week_low": {
            "label": "52-Week Low", "value": str(market_data.get("fifty_two_week_low")), "url": quote_url,
        },
        "historical_performance": {
            "label": "6-Month Performance",
            "value": f"{hist.get('start_price')} -> {hist.get('end_price')} ({hist.get('pct_change')}%)" if hist else "N/A",
            "url": history_url,
        },
    }

    for i, article in enumerate(market_data.get("recent_news") or []):
        headline = article.get("headline") or "Untitled"
        article_url = article.get("url") or quote_url
        registry[f"news_{i}"] = {
            "label": f"News: {headline[:60]}",
            "value": headline,
            "url": article_url,
        }

    return registry


def render_citations(text: str, registry: dict[str, dict[str, str]]) -> str:
    """
    Replace inline [citation_id] tags with small clickable footnote markers.
    The marker shows the underlying data point on hover AND links out to the
    real source page, so a user can click through and verify the claim
    themselves rather than just trusting the number. Unknown/invalid tags
    (the LLM citing an id that doesn't exist) are stripped rather than shown
    broken, since a dangling bracket looks like a bug, not a footnote.
    """

    def _replace(match: re.Match) -> str:
        cid = match.group(1)
        entry = registry.get(cid)
        if not entry:
            return ""
        tooltip = f"{entry['label']}: {entry['value']} (click to verify)".replace('"', "'")
        return (
            f'<sup><a href="{entry["url"]}" target="_blank" rel="noopener noreferrer" '
            f'title="{tooltip}" '
            f'style="color:#2563eb;font-weight:600;text-decoration:none;'
            f'border-bottom:1px dotted #2563eb;">[{cid}]</a></sup>'
        )

    return _CITATION_PATTERN.sub(_replace, text)


def extract_footnotes(text: str, registry: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    """
    Returns the ordered, de-duplicated list of {id, label, value, url} for
    every valid citation tag used in `text` — used to render a "Sources"
    list with real clickable links under each agent's message, since hover
    tooltips alone don't work on mobile/touch devices.
    """
    seen: set[str] = set()
    footnotes: list[dict[str, str]] = []
    for match in _CITATION_PATTERN.finditer(text):
        cid = match.group(1)
        if cid in seen:
            continue
        entry = registry.get(cid)
        if not entry:
            continue
        seen.add(cid)
        footnotes.append({"id": cid, "label": entry["label"], "value": entry["value"], "url": entry["url"]})
    return footnotes


def strip_citations(text: str) -> str:
    """Plain-text fallback (e.g. for Voice Mode) with citation tags removed."""
    return _CITATION_PATTERN.sub("", text).replace("  ", " ").strip()