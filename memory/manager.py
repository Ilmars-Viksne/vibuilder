import json
import logging
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(
        self,
        persist_path: str | Path = "agent_workspace/.vibuilder_memory.json",
    ):
        self.history = deque(maxlen=50)
        self.persist_path = Path(persist_path)
        self.current_step = 0
        self._load()

        if self.history:
            last_event = self.history[-1]
            self.current_step = last_event.get("step", len(self.history))

    def record(self, action: dict, result: Any) -> dict:
        self.current_step += 1

        event = {
            "step": self.current_step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "result": result,
        }

        self.history.append(event)
        self._save()
        return event

    def summary(self, limit: int = 10) -> str:
        if not self.history:
            return "(no memory yet)"

        recent = list(self.history)[-limit:]
        lines = []

        for event in recent:
            action = event.get("action", {})
            result = event.get("result", {})
            lines.append(
                f"Step {event.get('step')}: "
                f"{action.get('action')} -> "
                f"{self._shorten(result)}"
            )

        return "\n".join(lines)

    def _load(self) -> None:
        if not self.persist_path.exists():
            return

        try:
            data = json.loads(self.persist_path.read_text(encoding="utf-8"))
            for event in data:
                self.history.append(event)

        except Exception as exc:
            logger.warning("Failed to load memory file: %s", exc)

    def _save(self) -> None:
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        self.persist_path.write_text(
            json.dumps(list(self.history), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _shorten(self, value: Any, max_length: int = 300) -> str:
        text = json.dumps(value, ensure_ascii=False, default=str)
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
