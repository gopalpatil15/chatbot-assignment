# 🤖 Chatbot Assignment (Hugging Face + Streamlit)

A simple yet professional chatbot built with **Streamlit** for the frontend and **Hugging Face Transformers** for the backend.  
This project demonstrates clean architecture, modular design, and safe handling of secrets — perfect for portfolio and demo use.

---
## 🌐 Live Demo
Try the chatbot here: [Chatbot Live App](https://chatbot-assignment-6mpsfyz3tgvyvu35wejh5p.streamlit.app)

## 📂 Project Structure

```
chatbot-assignment/
│
├── app.py                  # Streamlit frontend (entry point)
├── requirements.txt        # Dependencies
├── README.md               # Project overview & setup guide
├── .gitignore              # Ignore secrets, cache, logs
│
├── backend/                # Core logic
│   ├── engine.py           # Hugging Face model interface
│   └── history_manager.py  # Chat history handling
│
├── storage/                # Persistence layer
│   └── json_store.py       # JSON-based storage for chat history
│
├── utils/                  # Utilities & configs
│   ├── config.py           # Centralized config (API keys, model, paths)
│   └── logger.py           # Logging setup
│
└── .streamlit/             # Local-only configs (ignored in Git)
    └── secrets.toml        # API keys (never pushed to GitHub)
```

---

## 🚀 Features

- **Streamlit UI** with chat-style interface  
- **Hugging Face Transformers** for text generation  
- **Config abstraction** via `utils/config.py`  
- **Chat history persistence** in JSON  
- **Clean repo hygiene** with `.gitignore`  

---

## ⚙️ Setup

### 1. Clone the Repo
```bash
git clone https://github.com/gopalpatil15/chatbot-assignment.git
cd chatbot-assignment
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.streamlit/secrets.toml` file (ignored by Git):

```toml
[openai]
api_key = "sk-your-openai-key"

[huggingface]
api_key = "hf-your-hf-token"   # optional if model is public
model = "HuggingFaceH4/zephyr-7b-beta"

[general]
max_turns = 5
history_file = "chat_history.json"
provider = "openai"   # or "huggingface"
```


Or set environment variables instead:
```bash
$env:HF_ACCESS_TOKEN="hf_your_token_here"
```

### 4. Run the App
```bash
streamlit run app.py
```

---

## 🧑‍💻 Usage

- Type a message in the chat box  
- The assistant responds using the Hugging Face model  
- Chat history is saved in `chat_history.json`  

---

## 🔒 Security Notes

- **Never commit API keys** — `.gitignore` ensures `secrets.toml` and `.env` are safe  
- Rotate tokens if accidentally exposed  

---

## 📌 Example

![Demo Screenshot]<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/b3ee00a8-ac1d-4ea5-b74d-8e8df4bb66c2" />
---


