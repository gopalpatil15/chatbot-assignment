import streamlit as st
from pathlib import Path

class Config:
    # API Keys
    OPENAI_KEY = st.secrets.get("api_keys", {}).get("openai", None)
    HF_TOKEN   = st.secrets.get("huggingface", {}).get("access_token", None)
    HF_MODEL   = st.secrets.get("huggingface", {}).get("model", "openchat/openchat-3.5-0106")

    # Chatbot settings
    MAX_TURNS   = st.secrets.get("chatbot", {}).get("max_turns", 5)
    HISTORY_FILE = Path(st.secrets.get("chatbot", {}).get("history_file", "chat_history.json"))
    MODEL       = st.secrets.get("chatbot", {}).get("model", "gpt-3.5-turbo")