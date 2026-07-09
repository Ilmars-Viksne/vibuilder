import logging

from agent.parsing import extract_json_array

logger = logging.getLogger(__name__)


class Planner:
    def create_plan(self, provider, goal: str) -> list[str]:
        prompt = (
            "Create a step-by-step project plan to achieve the following goal:\n\n"
            f"{goal}\n\n"
            "Return ONLY a valid JSON list of strings representing the steps. "
            "Do not include any prose or markdown formatting."
        )

        response = provider.chat(
            [
                {
                    "role": "system",
                    "content": "You are a precise software project planner.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        plan = extract_json_array(response)

        if not all(isinstance(step, str) for step in plan):
            raise ValueError("Planner response must be a JSON list of strings")

        logger.info("Created plan with %d steps", len(plan))
        return plan
