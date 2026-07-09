from pathlib import Path
import subprocess


class GitTools:
    def __init__(self, workspace_root: str | Path):
        self.workspace_root = Path(workspace_root)

    def init(self) -> dict:
        return self._run(["git", "init"])

    def commit(self, message: str) -> dict:
        add_result = self._run(["git", "add", "."])
        if add_result["returncode"] != 0:
            return add_result

        return self._run(["git", "commit", "-m", message])

    def _run(self, command: list[str]) -> dict:
        try:
            result = subprocess.run(
                command,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=60,
            )

            return {
                "status": "ok" if result.returncode == 0 else "failed",
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout[-10000:],
                "stderr": result.stderr[-10000:],
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "command": command,
                "error": "Timeout",
            }

        except Exception as exc:
            return {
                "status": "error",
                "command": command,
                "error": str(exc),
            }
