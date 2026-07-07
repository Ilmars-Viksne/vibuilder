import logging

logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self, workspace, runner, tests, git):
        self.workspace = workspace
        self.runner = runner
        self.tests = tests
        self.git = git

    def execute(self, action):
        kind = action.get("action")
        logger.debug(f"Executing action: {kind} with parameters: {action}")

        try:
            if kind == "create_folder":
                self.workspace.create_folder(action["path"])
                return "folder created"

            if kind == "create_file":
                self.workspace.create_file(action["path"], action.get("content", ""))
                return "file created"

            if kind == "edit_file":
                self.workspace.edit_file(action["path"], action.get("content", ""))
                return "file edited"

            if kind == "replace_text":
                self.workspace.replace_text(action["path"], action["search"], action["replace"])
                return "text replaced"

            if kind == "run_python":
                return self.runner.run(self.workspace.resolve(action["path"]))

            if kind == "run_tests":
                return self.tests.run_tests(self.workspace.root)

            if kind == "git_init":
                return self.git.init().stdout or "git initialized"

            if kind == "git_commit":
                return self.git.commit(action.get("message", "Commit by agent")).stdout or "committed"

            if kind == "finish":
                return "completed"

            raise ValueError(f"Unknown action: {kind}")
        except Exception as e:
            logger.error(f"Error executing action {kind}: {e}")
            return {"error": str(e)}
