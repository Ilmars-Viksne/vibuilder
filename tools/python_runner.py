import subprocess

class PythonRunner:
    def run(self, script_path):
        try:
            result = subprocess.run(
                ["python", str(script_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout", "stderr": "Execution exceeded 120 seconds"}
        except Exception as e:
            return {"error": str(e)}
