import logging
from agent.parsing import extract_json_array

logger = logging.getLogger(__name__)

class Planner:
    def create_plan(self, provider, goal):
        prompt = (
            "Create a step-by-step project plan to achieve the following goal:\n\n"
            f"{goal}\n\n"
            "Return ONLY a valid JSON list of strings representing the steps. "
            "Do not include any prose or markdown formatting."
        )
        response = provider.chat([{"role": "user", "content": prompt}])

        try:
            return extract_json_array(response)
        except Exception as e:
            logger.error(f"Planner JSON Parsing Error: {e}\nRaw Response: {response}")
            return [f"Execute task: {goal}"]
