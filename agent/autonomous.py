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
        logger.info("Starting task: %s", goal)

        plan = self.planner.create_plan(self.provider, goal)
        architecture = self.architect.design(self.provider, goal)

        feedback = "No feedback yet."
        final_action = None

        for step in range(1, max_steps + 1):
            context = self._build_context(
                goal=goal,
                plan=plan,
                architecture=architecture,
                feedback=feedback,
            )

            try:
                action = self.coder.next_action(self.provider, context)
            except Exception as exc:
                feedback = f"Failed to parse or validate action: {exc}"
                self.memory.record(
                    action={"action": "invalid"},
                    result={"error": feedback},
                )
                continue

            final_action = action

            if action["action"] == "finish":
                self.memory.record(
                    action=action,
                    result={"status": "finished"},
                )
                break

            result = self.executor.execute(action)
            self.memory.record(action=action, result=result)

            feedback = self._format_feedback(result)

            if action["action"] == "run_tests":
                test_review = self.tester.evaluate(self.provider, result)
                feedback = f"{feedback}\n\nTester feedback:\n{test_review}"

        review = self.reviewer.review(
            self.provider,
            list(self.memory.history),
        )

        return {
            "goal": goal,
            "plan": plan,
            "architecture": architecture,
            "last_action": final_action,
            "review": review,
            "history": list(self.memory.history),
        }

    def _build_context(
        self,
        goal: str,
        plan: list[str],
        architecture: str,
        feedback: str,
    ) -> str:
        plan_text = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan))

        return f"""
You are an autonomous coding agent.

Goal:
{goal}

Plan:
{plan_text}

Architecture:
{architecture}

Current Workspace Tree:
{TreeBuilder.build(self.workspace)}

Memory Recent Actions:
{self.memory.summary(limit=10)}

Last Feedback:
{feedback}

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
            return "\n".join(f"{k}: {v}" for k, v in result.items())
        return str(result)
