from pathlib import Path
import subprocess


class GitTools:
    def __init__(self, workspace_root: str | Path):
        self.workspace_root = Path(workspace_root)

    def init(self) -> dict:
        init_result = self._run(["git", "init"])
        if not init_result["success"]:
            return init_result

        # Configure local git user for the workspace
        self._run(["git", "config", "user.name", "Vibuilder Agent"])
        self._run(["git", "config", "user.email", "vibuilder@example.local"])

        return init_result

    def commit(self, message: str) -> dict:
        add_result = self._run(["git", "add", "."])
        if not add_result["success"]:
            return add_result

        commit_result = self._run(["git", "commit", "-m", message])
        return commit_result

    def _run(self, command: list[str]) -> dict:
        result = subprocess.run(
            command,
            cwd=str(self.workspace_root),
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )

        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
