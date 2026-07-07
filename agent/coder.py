import json
import re
import logging

logger = logging.getLogger(__name__)

class Coder:
    def next_action(self, provider, context):
        response = provider.chat([{"role": "system", "content": context}])

        # Robust JSON parsing to handle LLMs that wrap output in markdown
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\n', '', cleaned)
            cleaned = re.sub(r'\n```$', '', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Coder JSON Parsing Error: {e}\nRaw Response: {response}")
            return {"action": "finish"}
