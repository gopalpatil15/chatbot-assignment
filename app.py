import streamlit as st
from backend.engine import chat_with_model as chat_with_openai
from backend.history_manager import ChatMemory
from utils.config import Config
from storage.json_store import JSONStore
import time
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
# --- Custom CSS for Enhanced Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 5px 18px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background: rgba(255, 255, 255, 0.9);
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 5px;
        margin: 5px 0;
        max-width: 80%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .typing-indicator {
        display: inline-block;
        padding: 10px 15px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 18px 18px 18px 5px;
        margin: 5px 0;
    }
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #666;
        margin: 0 2px;
        animation: typing 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px;
        margin: 5px 0;
    }
    .control-panel {
        background: linear-gradient(180deg, #2d3748 0%, #4a5568 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
    .section-title {
        color: #fff;
        font-size: 1.2rem;
        margin-bottom: 15px;
        border-bottom: 2px solid #667eea;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "memory" not in st.session_state:
    st.session_state.memory = ChatMemory(max_turns=Config.MAX_TURNS)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Initialize JSON store
store = JSONStore(file_path=Config.HISTORY_FILE, max_turns=Config.MAX_TURNS)

# --- Main Layout with Control Panel on Left ---
left_col, right_col = st.columns([1, 2])

# ===== LEFT SIDEBAR - CONTROL PANEL =====
with left_col:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🎛️ Control Panel</div>', unsafe_allow_html=True)

    # --- Settings Section ---
    with st.expander("⚙️ Settings", expanded=True):
        st.write(f"**Model:** `{Config.MODEL}`")
        st.write(f"**Max Turns:** {Config.MAX_TURNS}")

        theme = st.selectbox("Theme", ["Dark", "Light"], index=0)
        st.session_state.dark_mode = (theme == "Dark")

        response_style = st.selectbox(
            "Response Style",
            ["Balanced", "Creative", "Precise", "Concise"],
            index=0
        )

        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make responses more creative, lower values more focused"
        )

    # --- Chat Management Section ---
    with st.expander("💬 Chat Management", expanded=True):
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.memory.clear()
            store.clear()
            st.session_state.messages = []
            st.rerun()

        if st.button("📤 Export Chat as JSON", use_container_width=True):
            chat_data = st.session_state.memory.as_messages()
            chat_json = json.dumps(chat_data, indent=2)
            st.download_button(
                label="Download Chat History",
                data=chat_json,
                file_name=f"chat_history_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True
            )

        uploaded_file = st.file_uploader("Import Chat JSON", type=['json'])
        if uploaded_file is not None:
            try:
                imported_data = json.load(uploaded_file)
                st.success("Chat history imported successfully!")
                if st.button("Apply Imported Chat", use_container_width=True):
                    st.session_state.memory.clear()
                    for msg in imported_data:
                        st.session_state.memory.add(msg["role"], msg["content"])
                    st.rerun()
            except Exception as e:
                st.error(f"Error importing file: {str(e)}")

    # --- Statistics Section ---
    with st.expander("📊 Statistics", expanded=True):
        total_messages = len(st.session_state.memory.as_messages())
        user_messages = len([m for m in st.session_state.memory.as_messages() if m["role"] == "user"])
        assistant_messages = total_messages - user_messages

        st.metric("Total Messages", total_messages)
        st.metric("Your Messages", user_messages)
        st.metric("AI Responses", assistant_messages)

        if Config.MAX_TURNS > 0:
            progress = min(total_messages / (Config.MAX_TURNS * 2), 1.0)
            st.progress(progress, text=f"Conversation: {total_messages}/{Config.MAX_TURNS * 2}")

    # --- System Info Section ---
    with st.expander("ℹ️ System Info", expanded=True):
        st.write("**Status:** ✅ Online")
        st.write("**Version:** 2.0.0")
        st.write("**Last Updated:** Today")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Response Time", "1.2s")
        with col2:
            st.metric("Accuracy", "98%")

        st.progress(75, text="System Load: 75%")

    st.markdown('</div>', unsafe_allow_html=True)

# ===== RIGHT MAIN AREA - CHAT INTERFACE =====
with right_col:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">🧠 AI Chat Assistant</h1>', unsafe_allow_html=True)
        st.markdown("### Your Intelligent Conversation Partner")

    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for msg in st.session_state.memory.as_messages():
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        if st.session_state.thinking:
            typing_html = '''
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
            '''
            st.markdown(typing_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    input_col1, input_col2, input_col3 = st.columns([4, 1, 1])

    with input_col1:
        prompt = st.text_input(
            "Type your message...",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="Ask me anything...",
            help="Press Enter or click Send to submit your message"
        )

    with input_col2:
        send_button = st.button("Send 🚀", use_container_width=True, type="primary")

    with input_col3:
        if st.button("Clear ✨", use_container_width=True):
            prompt = ""
            st.rerun()

    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    quick_prompt = None
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

    with quick_col1:
        if st.button("💡 Explain AI", use_container_width=True):
            quick_prompt = "Can you explain what artificial intelligence is in simple terms?"

    with quick_col2:
        if st.button("📝 Summarize", use_container_width=True):
            quick_prompt = "Can you summarize our conversation so far?"

    with quick_col3:
        if st.button("🔍 Help", use_container_width=True):
            quick_prompt = "What can you help me with? What are your capabilities?"

    with quick_col4:
        if st.button("🎯 Examples", use_container_width=True):
            quick_prompt = "Can you give me some examples of what I can ask you?"

# --- Chat Processing Logic ---
def process_message(user_input):
    st.session_state.memory.add("user", user_input)
    store.add("user", user_input)

    st.session_state.thinking = True
    st.rerun()

    try:
        reply = chat_with_openai(st.session_state.memory.as_messages())
        st.session_state.memory.add("assistant", reply)
        store.add("assistant", reply)
    except Exception as e:
        reply = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.memory.add("assistant", reply)
        store.add("assistant", reply)

    st.session_state.thinking = False

# Handle input
if send_button and prompt:
    process_message(prompt)
    st.rerun()

if quick_prompt:
    process_message(quick_prompt)
    st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 20px;">
    <small>Developed by Gopal Patil | Powered by Streamlit & Hugging Face</small>
</div>
""", unsafe_allow_html=True)