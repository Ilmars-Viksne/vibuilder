import logging

from agent.parsing import extract_json_object
from agent.validation import validate_action

logger = logging.getLogger(__name__)


class Coder:
    def next_action(self, provider, context: str) -> dict:
        response = provider.chat([{"role": "system", "content": context}])
        action = extract_json_object(response)
        validate_action(action)
        logger.info("Next action: %s", action.get("action"))
        return action
