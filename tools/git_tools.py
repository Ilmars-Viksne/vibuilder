import subprocess

class GitTools:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root

    def _run(self, args):
        return subprocess.run(
            ["git"] + args,
            cwd=self.workspace_root,
            capture_output=True,
            text=True
        )

    def init(self):
        return self._run(["init"])

    def commit(self, message):
        self._run(["add", "."])
        return self._run(["commit", "-m", message])

    def status(self):
        result = self._run(["status"])
        return result.stdout
