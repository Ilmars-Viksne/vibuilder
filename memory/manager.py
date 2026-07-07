import json
import logging
from collections import deque
from pathlib import Path

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, persist_path="agent_workspace/.vibuilder_memory.json"):
        self.history = deque(maxlen=50)
        self.persist_path = Path(persist_path)
        self._load()

    def add(self, action, result):
        self.history.append({
            "action": action,
            "result": result
        })
        self._save()

    def summary(self):
        return "\n".join([json.dumps(x) for x in self.history])

    def _save(self):
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(list(self.history), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    def _load(self):
        if self.persist_path.exists():
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history.extend(data)
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error loading memory: {e}")
                pass # Start fresh if file is corrupted
