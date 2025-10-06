import streamlit as st
from pathlib import Path
import json
from typing import List, Dict

from utils.config import Config
from backend.engine import chat_with_model

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="🤖 Smart Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Sidebar ----------------
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown(
    "Control your chatbot experience here. Choose provider, clear chat history, or adjust settings."
)

# Toggle provider
provider = st.sidebar.radio(
    "Choose model provider:",
    ["openai", "huggingface"],
    index=0 if Config.PROVIDER == "openai" else 1
)
Config.PROVIDER = provider

st.sidebar.markdown(f"**Active provider:** `{Config.PROVIDER}`")
if Config.PROVIDER == "huggingface":
    st.sidebar.markdown(f"**Model:** `{Config.HF_MODEL}`")
st.sidebar.markdown(f"**Max turns:** {Config.MAX_TURNS}")

if st.sidebar.button("🧹 Clear chat"):
    st.session_state.pop("messages", None)
    if Config.HISTORY_FILE.exists():
        Config.HISTORY_FILE.unlink(missing_ok=True)
    st.sidebar.success("Chat history cleared!")

# ---------------- Helpers ----------------
def load_history(file_path: Path) -> List[Dict[str, str]]:
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save_history(file_path: Path, messages: List[Dict[str, str]]):
    try:
        file_path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        st.warning(f"Could not save history: {e}")

def ensure_session_history():
    if "messages" not in st.session_state:
        st.session_state.messages = load_history(Config.HISTORY_FILE)

# ---------------- UI ----------------
st.title("🤖 Smart Chatbot")
st.markdown(
    "<p style='font-size:14px; color:gray;'>Switch between OpenAI and Hugging Face backends and enjoy a responsive chat experience.</p>",
    unsafe_allow_html=True
)

ensure_session_history()

# Display chat history with alternating colors
for m in st.session_state.messages:
    role = m["role"]
    if role == "user":
        st.chat_message("user").markdown(
            f"<div style='background-color:000; padding:10px; border-radius:8px;'>{m['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.chat_message("assistant").markdown(
            f"<div style='background-color:000; padding:10px; border-radius:8px;'>{m['content']}</div>",
            unsafe_allow_html=True
        )

# Input box
user_input = st.chat_input("💬 Type your message...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(
        f"<div style='background-color:000; padding:5px; border-radius:8px;'>{user_input}</div>",
        unsafe_allow_html=True
    )
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate assistant reply
    with st.chat_message("assistant"):
        st.markdown(
            "<div style='background-color:000; padding:5px; border-radius:8px;'>Generating response...</div>",
            unsafe_allow_html=True
        )
        try:
            reply = chat_with_model(st.session_state.messages)
            # Update last message
            st.chat_message("assistant").markdown(
                f"<div style='background-color:000; padding:5px; border-radius:8px;'>{reply}</div>",
                unsafe_allow_html=True
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
            save_history(Config.HISTORY_FILE, st.session_state.messages)
        except Exception as e:
            st.error(f" Error: {e}")
