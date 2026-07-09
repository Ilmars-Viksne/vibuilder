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
        self.history: deque[dict[str, Any]] = deque(maxlen=50)
        self.persist_path = Path(persist_path)
        self.current_step = 0
        self._load()

    def add(self, action: dict[str, Any], result: dict[str, Any]) -> None:
        self.current_step += 1

        entry = {
            "step": self.current_step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "result": result,
        }

        self.history.append(entry)
        self._save()

    def summary(self, limit: int = 10) -> str:
        recent = list(self.history)[-limit:]

        if not recent:
            return "<no previous actions>"

        lines = []
        for entry in recent:
            action_name = entry.get("action", {}).get("action", "<unknown>")
            success = entry.get("result", {}).get("success")
            lines.append(
                f"Step {entry.get('step')}: {action_name}, success={success}"
            )

        return "\n".join(lines)

    def to_list(self) -> list[dict[str, Any]]:
        return list(self.history)

    def _load(self) -> None:
        if not self.persist_path.exists():
            return

        try:
            data = json.loads(self.persist_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Memory file is invalid JSON; starting fresh")
            return

        self.current_step = int(data.get("current_step", 0))

        for entry in data.get("history", []):
            self.history.append(entry)

    def _save(self) -> None:
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_step": self.current_step,
            "history": list(self.history),
        }
        self.persist_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )
