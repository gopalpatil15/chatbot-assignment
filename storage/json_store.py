import json
from pathlib import Path

class JSONStore:
    def __init__(self, file_path="chat_history.json", max_turns=5):
        self.file_path = Path(file_path)
        self.max_turns = max_turns
        if not self.file_path.exists():
            self._save([])

    def _load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, history):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def add(self, role, content):
        history = self._load()
        history.append({"role": role, "content": content})
        # Keep only the last N turns (user+assistant = 2 messages per turn)
        if len(history) > self.max_turns * 2:
            history = history[-self.max_turns * 2:]
        self._save(history)

    def get(self):
        return self._load()

    def clear(self):
        self._save([])