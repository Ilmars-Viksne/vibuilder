import json
import logging
from typing import Any

from workspace.tree import TreeBuilder

logger = logging.getLogger(__name__)


class AutonomousAgent:
    def __init__(
        self,
        provider,
        workspace,
        executor,
        memory,
        planner,
        architect,
        coder,
        reviewer,
        tester,
    ):
        self.provider = provider
        self.workspace = workspace
        self.executor = executor
        self.memory = memory
        self.planner = planner
        self.architect = architect
        self.coder = coder
        self.reviewer = reviewer
        self.tester = tester

    def run(self, goal: str, max_steps: int = 50) -> dict[str, Any]:
        logger.info("Starting autonomous run")
        logger.info("Goal: %s", goal)

        plan = self.planner.create_plan(self.provider, goal)
        architecture = self.architect.design(self.provider, goal)

        last_feedback: Any = "<no feedback yet>"
        finished = False

        for step_index in range(1, max_steps + 1):
            context = self._build_context(
                goal=goal,
                plan=plan,
                architecture=architecture,
                last_feedback=last_feedback,
            )

            try:
                action = self.coder.next_action(self.provider, context)
            except Exception as exc:
                logger.exception("Failed to produce valid next action")
                last_feedback = {
                    "success": False,
                    "error": f"Failed to produce valid next action: {exc}",
                }
                continue

            result = self.executor.execute(action)
            self.memory.add(action, result)
            last_feedback = result

            if action.get("action") == "finish" or result.get("finished"):
                finished = True
                break

        review = self.reviewer.review(self.provider, self.memory.to_list())

        final_result = {
            "goal": goal,
            "finished": finished,
            "steps_used": self.memory.current_step,
            "plan": plan,
            "architecture": architecture,
            "review": review,
            "history": self.memory.to_list(),
        }

        logger.info("Autonomous run complete. finished=%s", finished)
        return final_result

    def _build_context(
        self,
        goal: str,
        plan: list[str],
        architecture: str,
        last_feedback: Any,
    ) -> str:
        return f"""
You are an autonomous coding agent.

Goal:
{goal}

Plan:
{json.dumps(plan, indent=2)}

Architecture:
{architecture}

Current Workspace Tree:
{TreeBuilder.build(self.workspace)}

Memory Recent Actions:
{self.memory.summary(limit=10)}

Last Feedback:
{self._format_feedback(last_feedback)}

Return ONLY valid JSON matching one allowed action schema.
Do not include Markdown fences like ```json.
Do not include prose, explanations, or comments.

Allowed actions:
- {{"action": "create_folder", "path": "path/to/dir"}}
- {{"action": "create_file", "path": "path/to/file", "content": "file content"}}
- {{"action": "edit_file", "path": "path/to/file", "content": "new content"}}
- {{"action": "replace_text", "path": "path/to/file", "search": "old text", "replace": "new text"}}
- {{"action": "run_python", "path": "path/to/script.py"}}
- {{"action": "run_tests"}}
- {{"action": "git_init"}}
- {{"action": "git_commit", "message": "commit message"}}
- {{"action": "finish"}}
""".strip()

    def _format_feedback(self, result: Any) -> str:
        if isinstance(result, dict):
            return "\n".join(f"{key}: {value}" for key, value in result.items())
        return str(result)
