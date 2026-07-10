# MarketMind

**Multi-Agent Debate System for Portfolio Risk Reasoning**

MarketMind is an AI-powered multi-agent investment analysis system that simulates
the decision-making process of an institutional investment committee. Instead of
producing a single buy/sell prediction, specialized AI agents (Bull, Bear, Macro)
debate a stock's merits, and a Synthesis agent produces a structured, explainable
risk assessment report.

## Problem Statement

Traditional AI-based finance applications mainly focus on predicting stock prices,
which is challenging due to market volatility, uncertainty, and the influence of
multiple economic factors. Single-model prediction systems often fail to provide
transparent reasoning behind investment decisions.

MarketMind solves this by having agents analyze a stock from different
perspectives — optimistic growth opportunities, potential risks, and macroeconomic
conditions — then debate, challenge each other's viewpoints, and generate a
structured risk report backed by real-time financial data.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Agent orchestration | LangGraph |
| LLM | Groq API |
| Market data | yfinance, Alpha Vantage / Finnhub |
| Frontend | Streamlit |

## Project Structure

```
market_mind/
├── README.md
├── requirements.txt
├── .env.example
├── app.py                      # Streamlit entry point
├── src/
│   ├── __init__.py
│   ├── config.py                # env vars, model + API config
│   ├── data/
│   │   ├── __init__.py
│   │   └── fetch_data.py        # yfinance / Alpha Vantage / Finnhub data collection
│   ├── llm/
│   │   ├── __init__.py
│   │   └── groq_client.py       # thin wrapper around the Groq chat completion API
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py        # shared agent behavior + prompt template
│   │   ├── bull_agent.py        # growth / opportunity case
│   │   ├── bear_agent.py        # risk / weakness case
│   │   ├── macro_agent.py       # macroeconomic conditions
│   │   └── synthesis_agent.py   # final structured risk report
│   └── graph/
│       ├── __init__.py
│       ├── state.py             # shared LangGraph state schema
│       └── debate_graph.py      # LangGraph workflow wiring the agents together
```

## Workflow

1. **User Input** — user enters a stock ticker (e.g. `TSLA`) in the Streamlit UI.
2. **Data Collection** — `src/data/fetch_data.py` pulls price, market cap, P/E,
   revenue growth, historical performance, fundamentals, and recent news.
3. **Multi-Agent Analysis** — Bull, Bear, and Macro agents each independently
   analyze the data from their perspective.
4. **Debate Process (LangGraph)** — agents see each other's arguments and refine
   their opinions over a configurable number of rounds.
5. **Synthesis Agent** — reviews the full debate transcript and produces a
   structured report: overall risk level, strengths, weaknesses, investment
   outlook, and a confidence score.
6. **Streamlit Dashboard** — displays the live debate transcript, individual agent
   opinions, risk analysis, and the final investment assessment.

## Setup

```bash
cd market_mind
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your API keys
```

## Run

```bash
streamlit run app.py
```

## Environment Variables

See `.env.example`:

- `GROQ_API_KEY` — required, powers all agents
- `ALPHA_VANTAGE_API_KEY` — optional, fundamentals/news fallback
- `FINNHUB_API_KEY` — optional, fundamentals/news fallback

## Disclaimer

MarketMind is a research/educational project. Nothing it outputs is financial
advice; it does not place trades and should not be used as the sole basis for
investment decisions.
