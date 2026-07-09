import json
import logging
from collections import deque
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, persist_path="agent_workspace/.vibuilder_memory.json"):
        self.history = deque(maxlen=50)
        self.persist_path = Path(persist_path)
        self.current_step = 0
        self._load()
        if self.history:
            # Estimate current step from last event
            last_event = self.history[-1]
            self.current_step = last_event.get("step", len(self.history))

    def add_event(self, phase, action, result):
        self.current_step += 1
        event = {
            "step": self.current_step,
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "action": action,
            "result": result
        }
        self.history.append(event)
        self._save()

    def add(self, action, result):
        """Legacy support for add method"""
        self.add_event("execute", action, result)

    def summary(self, limit=10):
        # Return last 'limit' events
        events = list(self.history)[-limit:]
        return "\n".join([json.dumps(x) for x in events])

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

    def clear(self):
        self.history.clear()
        self.current_step = 0
        if self.persist_path.exists():
            self.persist_path.unlink()
