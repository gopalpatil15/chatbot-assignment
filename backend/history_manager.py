class ChatMemory:
    def __init__(self, max_turns=5):
        self.max_turns = max_turns
        self.history = []  # list of dicts: {"role": "user"/"assistant", "content": str}

    def add(self, role, content):
        """Add a new message to history."""
        self.history.append({"role": role, "content": content})
        # Keep only the last N turns (user+assistant = 2 messages per turn)
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-self.max_turns * 2:]

    def get_context(self):
        """Return history as a plain text transcript."""
        return "\n".join([f"{m['role']}: {m['content']}" for m in self.history])

    def as_messages(self):
        """Return history in OpenAI/HF-friendly format."""
        return self.history

    def clear(self):
        """Reset the conversation."""
        self.history = []