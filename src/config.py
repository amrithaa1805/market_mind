"""
Central configuration for MarketMind.

Loads environment variables once so every module can import settings
from a single place instead of calling os.getenv() everywhere.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- LLM ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # --- Market data ---
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")

    # --- Debate settings ---
    DEBATE_ROUNDS: int = int(os.getenv("DEBATE_ROUNDS", "2"))

    def validate(self) -> list[str]:
        """Return a list of human-readable warnings for missing required config."""
        warnings = []
        if not self.GROQ_API_KEY:
            warnings.append(
                "GROQ_API_KEY is not set. Add it to your .env file — "
                "all agents require it to call the Groq LLM."
            )
        if not self.ALPHA_VANTAGE_API_KEY and not self.FINNHUB_API_KEY:
            warnings.append(
                "Neither ALPHA_VANTAGE_API_KEY nor FINNHUB_API_KEY is set. "
                "The system will still work using yfinance alone, but "
                "news/fundamentals coverage will be reduced."
            )
        return warnings


settings = Settings()
