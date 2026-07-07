import subprocess

class TestRunner:
    def run_tests(self, workspace_root):
        # Run pytest specifically inside the workspace directory
        try:
            result = subprocess.run(
                ["pytest", str(workspace_root)],
                capture_output=True,
                text=True
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"error": str(e)}
