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
{self.memory.summary()}

Last Feedback:
{feedback}

Return ONLY valid JSON.
Allowed actions:
- create_folder (path)
- create_file (path, content)
- edit_file (path, content)
- replace_text (path, search, replace)
- run_python (path)
- run_tests (none)
- git_init (none)
- git_commit (message)
- finish (none)
"""

    def run(self, goal, max_steps=50):
        logger.info("-> Planning phase...")
        plan = self.planner.create_plan(self.provider, goal)
        logger.debug(f"Plan: {plan}")

        logger.info("-> Architecture phase...")
        architecture = self.architect.design(self.provider, goal)
        logger.debug(f"Architecture: {architecture}")

        feedback = "Initial step."

        logger.info("-> Entering Coding Loop...")
        for step in range(max_steps):
            context = self.build_context(goal, plan, architecture, feedback)
            action = self.coder.next_action(self.provider, context)

            if action.get("action") == "finish":
                logger.info("-> Coding completed. Moving to verification...")
                break

            result = self.executor.execute(action)
            self.memory.add(action, result)
            feedback = str(result)

            logger.info(f"STEP {step + 1} | Action: {action.get('action')} -> {action.get('path', '')}")
            logger.debug(f"Result: {result}")

        logger.info("-> Testing phase...")
        test_results = self.executor.execute({"action": "run_tests"})
        test_evaluation = self.tester.evaluate(self.provider, test_results)
        logger.info(f"Test Evaluation:\n{test_evaluation}")

        logger.info("-> Review phase...")
        final_review = self.reviewer.review(self.provider, self.memory.summary())
        logger.info(f"Final Review:\n{final_review}")
