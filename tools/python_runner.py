from pathlib import Path
import subprocess


class PythonRunner:
    def run(self, script_path: str | Path) -> dict:
        script_path = Path(script_path)

        if not script_path.exists():
            raise FileNotFoundError(f"Python script not found: {script_path}")

        result = subprocess.run(
            ["python", str(script_path)],
            cwd=str(script_path.parent),
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )

        return {
            "command": f"python {script_path.name}",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
