from gtts import gTTS
from io import BytesIO

# Regional English accents for different agents.
# NOTE: keys must match the exact `role` strings the agents use
# (see src/agents/bull_agent.py, bear_agent.py, macro_agent.py,
# synthesis_agent.py) — "Bull Agent", not "Bull".
VOICE_MAP = {
    "Bull Agent": "com",          # American English
    "Bear Agent": "co.uk",        # British English
    "Macro Risk Agent": "com.au", # Australian English
    "Synthesis Agent": "co.uk",   # British English
}


def synthesize_speech(text: str, role: str = "Bull Agent") -> bytes:
    """
    Convert a single piece of text into speech using the accent
    assigned to that agent's role.
    """
    if not text.strip():
        return b""

    tld = VOICE_MAP.get(role, "com")

    tts = gTTS(
        text=text,
        lang="en",
        tld=tld,
        slow=False
    )

    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    return audio_buffer.read()


def synthesize_debate(turns) -> bytes:
    """
    Convert an entire debate transcript into one continuous audio clip,
    synthesizing EACH turn separately in its own agent's voice, then
    concatenating the resulting MP3 clips together.
    """
    if not turns:
        return b""

    combined = BytesIO()

    for turn in turns:
        role = turn.get("role", "Bull Agent")
        content = turn.get("content", "").strip()

        if not content:
            continue

        spoken_line = f"{role} says. {content}"
        clip = synthesize_speech(spoken_line, role=role)
        combined.write(clip)

    combined.seek(0)
    return combined.read()