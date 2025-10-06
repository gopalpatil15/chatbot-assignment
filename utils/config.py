import streamlit as st
from pathlib import Path

class Config:
    PROVIDER = st.secrets["general"].get("provider", "openai")

    # OpenAI
    OPENAI_KEY = st.secrets["openai"].get("api_key", None)

    # Hugging Face
    HF_MODEL = st.secrets["huggingface"].get("model", None)
    HF_TOKEN = st.secrets["huggingface"].get("api_key", None)

    # General
    MAX_TURNS = st.secrets["general"].get("max_turns", 5)
    HISTORY_FILE = Path(st.secrets["general"].get("history_file", "chat_history.json"))
