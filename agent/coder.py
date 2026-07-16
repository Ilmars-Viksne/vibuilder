import json
import logging

from agent.parsing import extract_json_object
from agent.validation import validate_action

logger = logging.getLogger(__name__)


class Coder:
    def __init__(self, max_repair_attempts: int = 2):
        self.max_repair_attempts = max_repair_attempts

    def next_action(self, provider, context: str) -> dict:
        response = provider.chat(
            [
                {
                    "role": "system",
                    "content": context,
                }
            ],
            temperature=0.0,
        )

        try:
            return self._parse_and_validate(response)
        except Exception as first_error:
            logger.warning("Initial action parse failed: %s", first_error)
            logger.debug("Invalid model response:\n%s", response)

            repaired_response = response

            for attempt in range(1, self.max_repair_attempts + 1):
                repair_prompt = self._build_repair_prompt(
                    invalid_response=repaired_response,
                    error=str(first_error),
                )

                repaired_response = provider.chat(
                    [
                        {
                            "role": "system",
                            "content": repair_prompt,
                        }
                    ],
                    temperature=0.0,
                )

                try:
                    return self._parse_and_validate(repaired_response)
                except Exception as repair_error:
                    logger.warning(
                        "Repair attempt %d failed: %s",
                        attempt,
                        repair_error,
                    )
                    first_error = repair_error

            raise ValueError(
                f"Failed to produce a valid action after "
                f"{self.max_repair_attempts} repair attempts: {first_error}"
            ) from first_error

    def _parse_and_validate(self, response: str) -> dict:
        if not response or not response.strip():
            raise ValueError("Provider returned an empty response")
        
        action = extract_json_object(response)
        validate_action(action)
        logger.info("Next action: %s", action.get("action"))
        return action

    def _build_repair_prompt(self, invalid_response: str, error: str) -> str:
        return f"""
You returned invalid JSON for an autonomous coding-agent action.

Parse/validation error:
{error}

Invalid response:
{invalid_response}

Return ONLY one valid JSON object.
Do not include Markdown fences.
Do not include prose.
Do not include comments.

The JSON object must match exactly one of these schemas:

{{"action": "create_folder", "path": "path/to/dir"}}
{{"action": "create_file", "path": "path/to/file", "content": "file content"}}
{{"action": "edit_file", "path": "path/to/file", "content": "new content"}}
{{"action": "replace_text", "path": "path/to/file", "search": "old text", "replace": "new text"}}
{{"action": "list_directory", "path": "path/to/dir"}}
{{"action": "read_file", "path": "path/to/file"}}
{{"action": "run_python", "path": "path/to/script.py"}}
{{"action": "run_tests"}}
{{"action": "git_init"}}
{{"action": "git_commit", "message": "commit message"}}
{{"action": "finish"}}

Tool rules:
- Use list_directory instead of ls or dir.
- Use read_file instead of cat or type.
- run_python accepts only an existing .py script path.
- Use run_tests to run pytest.
- Never place a shell command in a path field.

Important JSON rules:
- Escape all inner double quotes inside string values.
- Encode newlines as \\n inside string values.
- Do not use triple quotes.
- Do not use trailing commas.
- The entire response must be valid JSON.
""".strip()
