from pathlib import Path
import subprocess


class TestRunner:
    def run_tests(self, workspace_root: str | Path) -> dict:
        workspace_root = Path(workspace_root)

        try:
            result = subprocess.run(
                ["pytest", "-q", str(workspace_root)],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "status": "ok" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout[-10000:],
                "stderr": result.stderr[-10000:],
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Timeout",
                "stderr": "Tests exceeded 120 seconds",
            }

        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
            }
