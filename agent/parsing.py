import json
import re
import logging

logger = logging.getLogger(__name__)

def extract_json_object(text: str) -> dict:
    """Extracts a single JSON object from text, handling markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try finding the first '{' and last '}'
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))

def extract_json_array(text: str) -> list:
    """Extracts a JSON array from text, handling markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try finding the first '[' and last ']'
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))
