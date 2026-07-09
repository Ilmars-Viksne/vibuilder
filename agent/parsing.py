import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = _strip_markdown_fences(text)

    try:
        value = json.loads(cleaned)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    candidate = _extract_balanced_json(cleaned, "{", "}")
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON object: {exc}") from exc

    if not isinstance(value, dict):
        raise ValueError("Extracted JSON value is not an object")

    return value


def extract_json_array(text: str) -> list[Any]:
    cleaned = _strip_markdown_fences(text)

    try:
        value = json.loads(cleaned)
        if isinstance(value, list):
            return value
    except json.JSONDecodeError:
        pass

    candidate = _extract_balanced_json(cleaned, "[", "]")
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON array: {exc}") from exc

    if not isinstance(value, list):
        raise ValueError("Extracted JSON value is not an array")

    return value


def _strip_markdown_fences(text: str) -> str:
    cleaned = text.strip()

    fence_pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.match(fence_pattern, cleaned, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return cleaned


def _extract_balanced_json(text: str, opening: str, closing: str) -> str:
    start = text.find(opening)
    if start == -1:
        raise ValueError(f"No JSON starting with {opening!r} found")

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise ValueError(f"No balanced JSON ending with {closing!r} found")
