import logging

logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self, workspace, runner, tests, git):
        self.workspace = workspace
        self.runner = runner
        self.tests = tests
        self.git = git

    def execute(self, action: dict) -> dict:
        """
        Validates and dispatches the action to the appropriate handler.
        Returns a consistent result envelope.
        """
        if not isinstance(action, dict):
            return {
                "ok": False,
                "error": f"Invalid action format: expected dict, got {type(action).__name__}"
            }

        name = action.get("action")
        if not name:
            return {
                "ok": False,
                "error": "Missing 'action' field in request"
            }

        handlers = {
            "create_folder": self._create_folder,
            "create_file": self._create_file,
            "edit_file": self._edit_file,
            "replace_text": self._replace_text,
            "run_python": self._run_python,
            "run_tests": self._run_tests,
            "git_init": self._git_init,
            "git_commit": self._git_commit,
            "finish": self._finish,
        }

        handler = handlers.get(name)
        if not handler:
            return {
                "ok": False,
                "action": name,
                "error": f"Unknown action: {name}"
            }

        try:
            result = handler(action)
            if isinstance(result, dict) and "ok" in result:
                return result

            return {
                "ok": True,
                "action": name,
                "message": str(result),
                "data": result if isinstance(result, (dict, list)) else {}
            }
        except Exception as e:
            logger.error(f"Error executing action {name}: {e}")
            return {
                "ok": False,
                "action": name,
                "error": str(e)
            }

    def _create_folder(self, action):
        path = action.get("path")
        if not path: raise ValueError("Missing 'path'")
        self.workspace.create_folder(path)
        return f"Folder created: {path}"

    def _create_file(self, action):
        path = action.get("path")
        content = action.get("content", "")
        if not path: raise ValueError("Missing 'path'")
        self.workspace.create_file(path, content)
        return f"File created: {path}"

    def _edit_file(self, action):
        path = action.get("path")
        content = action.get("content", "")
        if not path: raise ValueError("Missing 'path'")
        self.workspace.edit_file(path, content)
        return f"File edited: {path}"

    def _replace_text(self, action):
        path = action.get("path")
        search = action.get("search")
        replace = action.get("replace")
        if not path or search is None or replace is None:
            raise ValueError("Missing 'path', 'search', or 'replace'")
        self.workspace.replace_text(path, search, replace)
        return f"Text replaced in {path}"

    def _run_python(self, action):
        path = action.get("path")
        if not path: raise ValueError("Missing 'path'")
        full_path = self.workspace.resolve_safe(path)
        result = self.runner.run(full_path)
        return {
            "ok": result.get("returncode") == 0 if "returncode" in result else False,
            "action": "run_python",
            "data": result
        }

    def _run_tests(self, action):
        result = self.tests.run_tests(self.workspace.root)
        return {
            "ok": result.get("returncode") == 0 if "returncode" in result else False,
            "action": "run_tests",
            "data": result
        }

    def _git_init(self, action):
        result = self.git.init()
        return {
            "ok": result.returncode == 0,
            "action": "git_init",
            "message": result.stdout or "Git initialized"
        }

    def _git_commit(self, action):
        message = action.get("message", "Commit by agent")
        result = self.git.commit(message)
        return {
            "ok": result.returncode == 0,
            "action": "git_commit",
            "message": result.stdout or "Committed changes"
        }

    def _finish(self, action):
        return {"ok": True, "action": "finish", "message": "Task completed"}
