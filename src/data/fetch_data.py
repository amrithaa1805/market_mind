"""
Step 2: Data Collection.

Pulls real-time / recent financial information for a ticker from:
  - yfinance (primary: price, market cap, P/E, historical performance, fundamentals)
  - Alpha Vantage (fallback/enrichment: company overview, news sentiment)
  - Finnhub (fallback/enrichment: company news)

Returns a single structured dict that is fed into the multi-agent debate.
"""
from __future__ import annotations

from typing import Any

import requests
import yfinance as yf

from src.config import settings


def _safe_get(d: dict, key: str, default=None):
    val = d.get(key, default)
    return val if val is not None else default


def fetch_yfinance_data(ticker: str) -> dict[str, Any]:
    """Pull core price/fundamentals/history data from yfinance."""
    stock = yf.Ticker(ticker)
    info = stock.info or {}

    hist = stock.history(period="6mo")
    historical_performance = None
    if not hist.empty:
        start_price = float(hist["Close"].iloc[0])
        end_price = float(hist["Close"].iloc[-1])
        pct_change = ((end_price - start_price) / start_price) * 100 if start_price else None
        historical_performance = {
            "period": "6mo",
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
            "pct_change": round(pct_change, 2) if pct_change is not None else None,
        }

    return {
        "ticker": ticker.upper(),
        "company_name": _safe_get(info, "longName", ticker.upper()),
        "current_price": _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice"),
        "market_cap": _safe_get(info, "marketCap"),
        "pe_ratio": _safe_get(info, "trailingPE"),
        "forward_pe": _safe_get(info, "forwardPE"),
        "revenue_growth": _safe_get(info, "revenueGrowth"),
        "profit_margins": _safe_get(info, "profitMargins"),
        "debt_to_equity": _safe_get(info, "debtToEquity"),
        "sector": _safe_get(info, "sector"),
        "industry": _safe_get(info, "industry"),
        "fifty_two_week_high": _safe_get(info, "fiftyTwoWeekHigh"),
        "fifty_two_week_low": _safe_get(info, "fiftyTwoWeekLow"),
        "historical_performance": historical_performance,
        "summary": _safe_get(info, "longBusinessSummary"),
    }


def fetch_alpha_vantage_overview(ticker: str) -> dict[str, Any]:
    """Optional enrichment: company overview + news sentiment from Alpha Vantage."""
    if not settings.ALPHA_VANTAGE_API_KEY:
        return {}
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json() or {}
    except requests.RequestException:
        return {}


def fetch_finnhub_news(ticker: str, limit: int = 5) -> list[dict[str, Any]]:
    """Optional enrichment: recent company news headlines from Finnhub."""
    if not settings.FINNHUB_API_KEY:
        return []
    try:
        import datetime

        today = datetime.date.today()
        month_ago = today - datetime.timedelta(days=30)
        url = "https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": ticker,
            "from": month_ago.isoformat(),
            "to": today.isoformat(),
            "token": settings.FINNHUB_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json() or []
        return [
            {"headline": a.get("headline"), "summary": a.get("summary"), "url": a.get("url")}
            for a in articles[:limit]
        ]
    except requests.RequestException:
        return []


def collect_market_data(ticker: str) -> dict[str, Any]:
    """
    Orchestrates Step 2 of the workflow: gather everything the agents need
    in one call.
    """
    data = fetch_yfinance_data(ticker)
    data["alpha_vantage_overview"] = fetch_alpha_vantage_overview(ticker)
    data["recent_news"] = fetch_finnhub_news(ticker)
    return data
