import logging
from workspace.tree import TreeBuilder

logger = logging.getLogger(__name__)

class AutonomousAgent:
    def __init__(self, provider, workspace, executor, memory, planner, architect, coder, reviewer, tester):
        self.provider = provider
        self.workspace = workspace
        self.executor = executor
        self.memory = memory
        self.planner = planner
        self.architect = architect
        self.coder = coder
        self.reviewer = reviewer
        self.tester = tester

    def build_context(self, goal, plan, architecture, feedback):
        return f"""
You are an autonomous coding agent.

Goal: {goal}
Plan: {plan}
Architecture: {architecture}

Current Workspace Tree:
{TreeBuilder.build(self.workspace)}

Memory (Recent Actions):
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
"""

    def run(self, goal, max_steps=50):
        logger.info(f"Starting task: {goal}")

        logger.info("-> Planning phase...")
        plan = self.planner.create_plan(self.provider, goal)
        logger.info(f"Plan created: {plan}")

        logger.info("-> Architecture phase...")
        architecture = self.architect.design(self.provider, goal)
        logger.debug(f"Architecture: {architecture}")

        feedback = "Initial step."

        logger.info("-> Entering Coding Loop...")
        for step in range(max_steps):
            context = self.build_context(goal, plan, architecture, feedback)
            action = self.coder.next_action(self.provider, context)

            if action.get("action") == "finish":
                logger.info("-> Coder indicated completion.")
                self.memory.add_event("execute", action, "Task finished by agent")
                break

            if action.get("action") == "error":
                logger.warning(f"Coder error: {action.get('message')}")
                feedback = f"Error: {action.get('message')}"
                self.memory.add_event("error", action, feedback)
                continue

            logger.info(f"STEP {step + 1}/{max_steps} | Action: {action.get('action')} -> {action.get('path', '')}")

            result = self.executor.execute(action)
            self.memory.add_event("execute", action, result)

            if result.get("ok"):
                feedback = result.get("message", "Success")
                logger.info(f"Result: SUCCESS - {feedback}")
            else:
                feedback = f"Failure: {result.get('error')}"
                logger.warning(f"Result: FAILED - {feedback}")

        else:
            logger.warning(f"Reached maximum steps ({max_steps}) without finishing.")

        logger.info("-> Verification phase...")
        test_results = self.executor.execute({"action": "run_tests"})
        test_evaluation = self.tester.evaluate(self.provider, test_results)
        logger.info(f"Test Evaluation:\n{test_evaluation}")

        logger.info("-> Review phase...")
        final_review = self.reviewer.review(self.provider, self.memory.summary(limit=50))
        logger.info(f"Final Review:\n{final_review}")

        return {
            "goal": goal,
            "steps_taken": step + 1 if 'step' in locals() else 0,
            "test_evaluation": test_evaluation,
            "final_review": final_review
        }
