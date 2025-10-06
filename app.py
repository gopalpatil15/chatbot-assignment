# app.py
import streamlit as st
from pathlib import Path
import json
from typing import List, Dict

from utils.config import Config
from huggingface_hub import login
from transformers import pipeline

st.set_page_config(page_title="Chatbot (Hugging Face)", page_icon="🤖", layout="centered")

# ---------- Sidebar ----------
st.sidebar.title("Settings")
st.sidebar.markdown("Model and history controls")

st.sidebar.write(f"• Using Hugging Face model: `{Config.HF_MODEL}`")
st.sidebar.write(f"• Max turns: {Config.MAX_TURNS}")

if st.sidebar.button("Clear chat history"):
    st.session_state.pop("messages", None)
    if Config.HISTORY_FILE.exists():
        try:
            Config.HISTORY_FILE.unlink()
        except Exception:
            pass
    st.sidebar.success("Chat history cleared.")


# ---------- HF init (lazy, one-time) ----------
def get_hf_pipeline():
    if "hf_pipeline" not in st.session_state:
        try:
            if Config.HF_TOKEN:
                login(Config.HF_TOKEN)
            st.session_state.hf_pipeline = pipeline(
                "text-generation",
                model=Config.HF_MODEL,
            )
        except Exception as e:
            st.error(f"Failed to initialize Hugging Face model `{Config.HF_MODEL}`: {e}")
            st.stop()
    return st.session_state.hf_pipeline


# ---------- History helpers ----------
def load_history(file_path: Path) -> List[Dict[str, str]]:
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
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


# ---------- Prompt formatting ----------
def history_to_prompt(messages: List[Dict[str, str]]) -> str:
    # Simple chat-style prompt; many HF instruct models respond well to this
    turns = []
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        turns.append(f"{role}: {m['content']}")
    turns.append("Assistant:")
    return "\n\n".join(turns)


# ---------- App UI ----------
st.title("🤖 Chatbot (Hugging Face)")
st.caption("Powered by Transformers — no OpenAI required.")

ensure_session_history()
hf = get_hf_pipeline()

# Display existing messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat input
user_input = st.chat_input("Type your message…")

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Trim to last N turns (user+assistant pairs). Keep system-free simplicity.
    # We'll keep last 2*MAX_TURNS messages.
    max_msgs = max(2 * Config.MAX_TURNS, 2)
    st.session_state.messages = st.session_state.messages[-max_msgs:]

    # Build prompt and query HF
    prompt = history_to_prompt(st.session_state.messages)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            out = hf(
                prompt,
                max_new_tokens=300,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
            )
            text = out[0]["generated_text"]

            # Heuristic: many instruct models echo the prompt; strip it out if present
            assistant_reply = text[len(prompt):].strip() if text.startswith(prompt) else text.strip()

            st.markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            save_history(Config.HISTORY_FILE, st.session_state.messages)

        except Exception as e:
            st.error(f"Generation failed: {e}")