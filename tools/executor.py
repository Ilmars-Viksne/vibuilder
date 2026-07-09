import logging

from agent.validation import validate_action

logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, workspace, runner, tests, git):
        self.workspace = workspace
        self.runner = runner
        self.tests = tests
        self.git = git

    def execute(self, action: dict) -> dict:
        validate_action(action)

        action_name = action["action"]
        logger.info("Executing action: %s", action_name)

        try:
            if action_name == "create_folder":
                return self.workspace.create_folder(action["path"])

            if action_name == "create_file":
                return self.workspace.create_file(
                    action["path"],
                    action["content"],
                )

            if action_name == "edit_file":
                return self.workspace.write_file(
                    action["path"],
                    action["content"],
                )

            if action_name == "replace_text":
                return self.workspace.replace_text(
                    action["path"],
                    action["search"],
                    action["replace"],
                )

            if action_name == "run_python":
                script = self.workspace.resolve(action["path"])
                return self.runner.run(script)

            if action_name == "run_tests":
                return self.tests.run_tests(self.workspace.root)

            if action_name == "git_init":
                return self.git.init()

            if action_name == "git_commit":
                return self.git.commit(action["message"])

            if action_name == "finish":
                return {"status": "finished"}

            raise ValueError(f"Unsupported action: {action_name}")

        except Exception as exc:
            logger.exception("Action failed: %s", action_name)
            return {
                "status": "error",
                "action": action_name,
                "error": str(exc),
            }
