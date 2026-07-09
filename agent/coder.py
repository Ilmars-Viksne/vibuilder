import logging
from agent.parsing import extract_json_object

logger = logging.getLogger(__name__)

class Coder:
    def next_action(self, provider, context):
        response = provider.chat([{"role": "system", "content": context}])

        try:
            return extract_json_object(response)
        except Exception as e:
            logger.error(f"Coder JSON Parsing Error: {e}\nRaw Response: {response}")
            # If parsing fails, try to return an error that might be fed back
            return {"action": "error", "message": f"Failed to parse your response as JSON: {e}"}
