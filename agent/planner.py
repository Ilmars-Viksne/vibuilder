import json
import re
import logging

logger = logging.getLogger(__name__)

class Planner:
    def create_plan(self, provider, goal):
        prompt = f"Create a step-by-step project plan to achieve the following goal:\n\n{goal}\n\nReturn the plan as a JSON list of strings."
        response = provider.chat([{"role": "user", "content": prompt}])

        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\n', '', cleaned)
            cleaned = re.sub(r'\n```$', '', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Planner JSON Parsing Error: {e}\nRaw Response: {response}")
            return [f"Execute task: {goal}"]
