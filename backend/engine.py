import logging
from transformers import pipeline
from huggingface_hub import login
from openai import OpenAI
from utils.config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_hf_pipeline = None
_openai_client = None


def _init_huggingface():
    global _hf_pipeline
    if _hf_pipeline is None:
        try:
            if Config.HF_TOKEN:
                login(Config.HF_TOKEN)
            _hf_pipeline = pipeline(
                "text-generation",
                model=Config.HF_MODEL,
                token=Config.HF_TOKEN
            )
            logger.info(f"Hugging Face model loaded: {Config.HF_MODEL}")
        except Exception as e:
            logger.error(f"Failed to init Hugging Face: {e}")
            raise
    return _hf_pipeline


def _init_openai():
    global _openai_client
    if _openai_client is None:
        try:
            _openai_client = OpenAI(api_key=Config.OPENAI_KEY)
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to init OpenAI: {e}")
            raise
    return _openai_client


def _history_to_prompt(messages):
    turns = []
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        turns.append(f"{role}: {m['content']}")
    turns.append("Assistant:")
    return "\n\n".join(turns)


def chat_with_model(messages_or_prompt):
    try:
        # Build prompt
        if isinstance(messages_or_prompt, list):
            prompt = _history_to_prompt(messages_or_prompt)
        else:
            prompt = str(messages_or_prompt)

        if Config.PROVIDER == "huggingface":
            hf_chatbot = _init_huggingface()
            response = hf_chatbot(
                prompt,
                max_new_tokens=300,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
            )
            text = response[0]["generated_text"]
            return text[len(prompt):].strip() if text.startswith(prompt) else text.strip()

        elif Config.PROVIDER == "openai":
            client = _init_openai()
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or whichever model you want
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        else:
            return f"Unknown provider: {Config.PROVIDER}"

    except Exception as e:
        logger.error(f"Chat error with {Config.PROVIDER}: {e}")
        return f"Error using {Config.PROVIDER}: {e}"
