"""
Shared state schema passed between nodes in the LangGraph debate workflow.
"""
from __future__ import annotations

from typing import Any, TypedDict


class DebateTurn(TypedDict):
    role: str
    content: str


class DebateState(TypedDict, total=False):
    ticker: str
    market_data: dict[str, Any]
    transcript: list[DebateTurn]
    round: int
    max_rounds: int
    report: dict[str, Any]
