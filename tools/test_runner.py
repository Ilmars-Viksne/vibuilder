from pathlib import Path
import subprocess


class TestRunner:
    def run_tests(self, workspace_root: str | Path) -> dict:
        workspace_root = Path(workspace_root)

        result = subprocess.run(
            ["python", "-m", "pytest", "-q"],
            cwd=str(workspace_root),
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )

        return {
            "command": "python -m pytest -q",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
