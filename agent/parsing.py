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
    value = json.loads(candidate)

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
    value = json.loads(candidate)

    if not isinstance(value, list):
        raise ValueError("Extracted JSON value is not an array")

    return value


def _strip_markdown_fences(text: str) -> str:
    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # Handles accidental responses like:
    # json
    # {"a": 1}
    cleaned = re.sub(
        r"^json\s*\n",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned.strip()


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
            return text[start:index + 1]

    raise ValueError("No balanced JSON value found")
