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
                path = self.workspace.create_folder(action["path"])
                return {
                    "success": True,
                    "action": action_name,
                    "path": str(path),
                }

            if action_name == "create_file":
                path = self.workspace.write_file(action["path"], action["content"])
                return {
                    "success": True,
                    "action": action_name,
                    "path": str(path),
                }

            if action_name == "edit_file":
                path = self.workspace.write_file(action["path"], action["content"])
                return {
                    "success": True,
                    "action": action_name,
                    "path": str(path),
                }

            if action_name == "replace_text":
                path = self.workspace.replace_text(
                    action["path"],
                    action["search"],
                    action["replace"],
                )
                return {
                    "success": True,
                    "action": action_name,
                    "path": str(path),
                }

            if action_name == "run_python":
                script_path = self.workspace.resolve(action["path"])
                result = self.runner.run(script_path)
                result["action"] = action_name
                return result

            if action_name == "run_tests":
                result = self.tests.run_tests(self.workspace.root)
                result["action"] = action_name
                return result

            if action_name == "git_init":
                result = self.git.init()
                result["action"] = action_name
                return result

            if action_name == "git_commit":
                result = self.git.commit(action["message"])
                result["action"] = action_name
                return result

            if action_name == "finish":
                return {
                    "success": True,
                    "action": action_name,
                    "finished": True,
                }

            raise ValueError(f"Unhandled action: {action_name}")

        except Exception as exc:
            logger.exception("Action failed: %s", action_name)
            return {
                "success": False,
                "action": action_name,
                "error": str(exc),
            }
