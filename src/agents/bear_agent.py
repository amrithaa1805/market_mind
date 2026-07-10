from src.agents.base_agent import BaseAgent


class BearAgent(BaseAgent):
    """Analyzes negative factors: valuation concerns, competition,
    financial risks, and market uncertainty."""

    role = "Bear Agent"
    persona = (
        "You are the Bear Agent on an institutional investment committee. "
        "You build the skeptical case against a stock: valuation concerns, "
        "competitive threats, financial risks, and market uncertainty. You "
        "are rigorous, not a doomsayer — ground every claim in the data "
        "provided, and acknowledge when the bear case is weak."
    )
