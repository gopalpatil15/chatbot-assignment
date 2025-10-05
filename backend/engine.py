import logging
from transformers import pipeline
from huggingface_hub import login
from utils.config import Config

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize Hugging Face pipeline lazily
_hf_pipeline = None


def _init_huggingface():
    """Authenticate and initialize Hugging Face pipeline once."""
    global _hf_pipeline
    if _hf_pipeline is None:
        try:
            if Config.HF_TOKEN:
                login(Config.HF_TOKEN)
            _hf_pipeline = pipeline(
                "text-generation",
                model=Config.HF_MODEL,
            )
            logger.info(f"Hugging Face model loaded: {Config.HF_MODEL}")
        except Exception as e:
            logger.error(f"Failed to init Hugging Face: {e}")
            raise
    return _hf_pipeline


def _history_to_prompt(messages):
    """Convert chat history into a single prompt string."""
    turns = []
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        turns.append(f"{role}: {m['content']}")
    turns.append("Assistant:")  # cue the model to continue
    return "\n\n".join(turns)


def chat_with_model(messages_or_prompt):
    """
    Chat interface using Hugging Face only.
    Accepts either:
      - a list of dicts [{"role": "user"/"assistant", "content": "..."}]
      - or a plain string prompt
    """
    try:
        hf_chatbot = _init_huggingface()

        if isinstance(messages_or_prompt, list):
            prompt = _history_to_prompt(messages_or_prompt)
        else:
            prompt = str(messages_or_prompt)

        response = hf_chatbot(
            prompt,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
        )

        text = response[0]["generated_text"]

        # Strip echoed prompt if model repeats it
        return text[len(prompt):].strip() if text.startswith(prompt) else text.strip()

    except Exception as e:
        logger.error(f"Chat error with Hugging Face model {Config.HF_MODEL}: {e}")
        return f"Error using Hugging Face model {Config.HF_MODEL}: {e}"