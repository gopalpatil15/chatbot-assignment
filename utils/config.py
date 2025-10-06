import streamlit as st
from pathlib import Path


class Config:
    """Centralized configuration loaded from Streamlit Secrets."""

    # --- API Keys ---
    OPENAI_KEY = (
        st.secrets.get("api_keys", {}).get("openai", None)
    )
    HF_TOKEN = (
        st.secrets.get("huggingface", {}).get("access_token", None)
    )
    HF_MODEL = (
        st.secrets.get("huggingface", {}).get("model", "microsoft/DialoGPT-medium")  # ✅ lightweight default
    )

    # --- Chatbot Settings ---
    MAX_TURNS = (
        st.secrets.get("chatbot", {}).get("max_turns", 5)
    )
    HISTORY_FILE = Path(
        st.secrets.get("chatbot", {}).get("history_file", "chat_history.json")
    )

    # --- Optional for OpenAI fallback ---
    MODEL = (
        st.secrets.get("chatbot", {}).get("model", "gpt-3.5-turbo")
    )
