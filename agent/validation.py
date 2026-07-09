from pathlib import PurePosixPath


ALLOWED_ACTIONS = {
    "create_folder": {"path"},
    "create_file": {"path", "content"},
    "edit_file": {"path", "content"},
    "replace_text": {"path", "search", "replace"},
    "run_python": {"path"},
    "run_tests": set(),
    "git_init": set(),
    "git_commit": {"message"},
    "finish": set(),
}


PATH_FIELDS = {"path"}


def validate_action(action: dict) -> None:
    if not isinstance(action, dict):
        raise ValueError("Action must be a JSON object")

    action_name = action.get("action")
    if not isinstance(action_name, str):
        raise ValueError("Action must contain a string 'action' field")

    if action_name not in ALLOWED_ACTIONS:
        raise ValueError(f"Unknown action: {action_name}")

    required_fields = ALLOWED_ACTIONS[action_name]
    missing = required_fields - set(action)
    if missing:
        raise ValueError(
            f"Action '{action_name}' is missing required fields: "
            f"{', '.join(sorted(missing))}"
        )

    for field in required_fields:
        if field == "action":
            continue
        if not isinstance(action[field], str):
            raise ValueError(f"Field '{field}' must be a string")

    for field in PATH_FIELDS:
        if field in action:
            _validate_relative_safe_path(action[field])

    unexpected = set(action) - required_fields - {"action"}
    if unexpected:
        raise ValueError(
            f"Action '{action_name}' contains unexpected fields: "
            f"{', '.join(sorted(unexpected))}"
        )


def _validate_relative_safe_path(path: str) -> None:
    if not path:
        raise ValueError("Path must not be empty")

    pure_path = PurePosixPath(path)

    if pure_path.is_absolute():
        raise ValueError(f"Absolute paths are not allowed: {path}")

    if any(part == ".." for part in pure_path.parts):
        raise ValueError(f"Path traversal is not allowed: {path}")

    if any(part == "" for part in pure_path.parts):
        raise ValueError(f"Invalid path: {path}")
