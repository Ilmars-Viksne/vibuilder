from pathlib import Path
import subprocess


class PythonRunner:
    def run(self, script_path: str | Path) -> dict:
        script_path = Path(script_path)

        try:
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(script_path.parent),
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
                "stderr": "Execution exceeded 120 seconds",
            }

        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
            }
