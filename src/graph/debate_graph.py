"""
Step 3 & 4: Multi-Agent Analysis + Debate Process, orchestrated with LangGraph.

Graph shape:

    collect_data -> bull -> bear -> macro -> [loop back to bull for N rounds] -> synthesis -> END

Each of bull/bear/macro appends one DebateTurn to the shared transcript per
round; after `max_rounds` rounds the graph routes to the synthesis node.
"""
from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from src.agents.bear_agent import BearAgent
from src.agents.bull_agent import BullAgent
from src.agents.macro_agent import MacroRiskAgent
from src.agents.synthesis_agent import synthesize
from src.config import settings
from src.data.fetch_data import collect_market_data
from src.graph.state import DebateState

bull_agent = BullAgent()
bear_agent = BearAgent()
macro_agent = MacroRiskAgent()


def collect_data_node(state: DebateState) -> DebateState:
    market_data = collect_market_data(state["ticker"])
    return {"market_data": market_data, "transcript": [], "round": 0}


def bull_node(state: DebateState) -> DebateState:
    argument = bull_agent.analyze(state["market_data"], state["transcript"])
    turn = {"role": bull_agent.role, "content": argument}
    return {"transcript": state["transcript"] + [turn]}


def bear_node(state: DebateState) -> DebateState:
    argument = bear_agent.analyze(state["market_data"], state["transcript"])
    turn = {"role": bear_agent.role, "content": argument}
    return {"transcript": state["transcript"] + [turn]}


def macro_node(state: DebateState) -> DebateState:
    argument = macro_agent.analyze(state["market_data"], state["transcript"])
    turn = {"role": macro_agent.role, "content": argument}
    new_round = state.get("round", 0) + 1
    return {"transcript": state["transcript"] + [turn], "round": new_round}


def synthesis_node(state: DebateState) -> DebateState:
    report = synthesize(state["market_data"], state["transcript"])
    return {"report": report}


def _should_continue_debate(state: DebateState) -> str:
    max_rounds = state.get("max_rounds", settings.DEBATE_ROUNDS)
    if state.get("round", 0) < max_rounds:
        return "bull"
    return "synthesis"


def build_debate_graph():
    graph = StateGraph(DebateState)

    graph.add_node("collect_data", collect_data_node)
    graph.add_node("bull", bull_node)
    graph.add_node("bear", bear_node)
    graph.add_node("macro", macro_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("collect_data")
    graph.add_edge("collect_data", "bull")
    graph.add_edge("bull", "bear")
    graph.add_edge("bear", "macro")
    graph.add_conditional_edges(
        "macro",
        _should_continue_debate,
        {"bull": "bull", "synthesis": "synthesis"},
    )
    graph.add_edge("synthesis", END)

    return graph.compile()


def run_debate(ticker: str, max_rounds: int | None = None) -> dict[str, Any]:
    """
    Convenience entry point used by the Streamlit app: runs the full
    workflow for a ticker and returns the final state (market data,
    full transcript, and synthesized report).
    """
    app = build_debate_graph()
    initial_state: DebateState = {
        "ticker": ticker.upper(),
        "max_rounds": max_rounds or settings.DEBATE_ROUNDS,
    }
    return app.invoke(initial_state)
