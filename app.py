"""
Step 6: Streamlit Dashboard.

Entry point for MarketMind. Run with:

    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from src.config import settings
from src.graph.debate_graph import run_debate
from src.audio.tts import synthesize_debate, synthesize_speech

st.set_page_config(page_title="MarketMind", page_icon="📊", layout="wide")

st.title("📊 MarketMind")
st.caption("Multi-Agent Debate System for Portfolio Risk Reasoning")

for warning in settings.validate():
    st.warning(warning)

with st.sidebar:
    st.header("Settings")

    ticker = st.text_input(
        "Stock Ticker",
        value="TSLA"
    ).strip().upper()

    rounds = st.slider(
        "Debate Rounds",
        min_value=1,
        max_value=5,
        value=settings.DEBATE_ROUNDS
    )

    voice_mode = st.toggle(
        "🔊 Voice Mode",
        value=False
    )

    run_clicked = st.button(
        "Run Debate",
        type="primary",
        use_container_width=True
    )

if run_clicked and ticker:
    with st.spinner(f"Collecting data and running the investment committee debate for {ticker}..."):
        try:
            result = run_debate(ticker, max_rounds=rounds)
        except Exception as exc:
            st.error(f"Debate failed: {exc}")
            st.stop()

    market_data = result.get("market_data", {})
    transcript = result.get("transcript", [])
    report = result.get("report", {})

    # --- Snapshot ---
    st.subheader(f"{market_data.get('company_name', ticker)} ({ticker})")
    cols = st.columns(4)
    cols[0].metric("Price", market_data.get("current_price"))
    cols[1].metric("P/E Ratio", market_data.get("pe_ratio"))
    cols[2].metric("Market Cap", market_data.get("market_cap"))
    hist = market_data.get("historical_performance") or {}
    cols[3].metric("6M Change", f"{hist.get('pct_change')}%" if hist.get("pct_change") is not None else "N/A")

    # --- Live debate transcript ---
    st.subheader("🗣️ Live Debate Transcript")
    role_icons = {
        "Bull Agent": "🐂",
        "Bear Agent": "🐻",
        "Macro Risk Agent": "🌐",
    }
    for turn in transcript:
        icon = role_icons.get(turn["role"], "🤖")
        with st.chat_message("assistant"):
            st.markdown(f"**{icon} {turn['role']}:** {turn['content']}")
    if voice_mode:
        try:
            audio_bytes = synthesize_debate(transcript)

            if audio_bytes:
                st.markdown("### 🔊 Debate Audio")
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

        except Exception as e:
            st.warning(f"Voice Mode unavailable: {e}")

    # --- Final risk assessment ---
    st.subheader("📋 Final Investment Assessment")
    if report.get("parse_error"):
        st.warning("The synthesis agent's output could not be fully parsed as structured JSON.")
        st.write(report.get("investment_outlook"))
    else:
        risk_level = report.get("overall_risk_level", "Unknown")
        risk_color = {"Low": "green", "Medium": "orange", "High": "red"}.get(risk_level, "gray")
        st.markdown(f"**Overall Risk Level:** :{risk_color}[{risk_level}]")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Strengths**")
            for s in report.get("strengths", []):
                st.markdown(f"- {s}")
        with col_b:
            st.markdown("**Weaknesses**")
            for w in report.get("weaknesses", []):
                st.markdown(f"- {w}")

        st.markdown("**Investment Outlook**")
        st.write(report.get("investment_outlook", ""))

        confidence = report.get("confidence_score")
        if confidence is not None:
            st.progress(min(max(int(confidence), 0), 100) / 100, text=f"Confidence Score: {confidence}/100")
        
        if voice_mode:
            try:
                verdict = f"""Committee verdict.

                Overall risk level is {risk_level}.

                {report.get("investment_outlook", "")}

                Confidence score is {confidence} out of 100.
                """

                verdict_audio = synthesize_speech(
                    verdict,
                    role="Synthesis Agent"
                )

                st.markdown("### 🎙 Committee Verdict")

                st.audio(
                    verdict_audio,
                    format="audio/mp3",
                    autoplay=False
                )

            except Exception as e:
                st.warning(f"Unable to generate verdict narration: {e}")

elif run_clicked and not ticker:
    st.error("Please enter a stock ticker.")
else:
    st.info("Enter a ticker in the sidebar and click **Run Debate** to start the investment committee.")
