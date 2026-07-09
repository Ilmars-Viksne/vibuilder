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


def validate_action(action: dict) -> None:
    if not isinstance(action, dict):
        raise ValueError("Action must be a JSON object")

    action_name = action.get("action")
    if action_name not in ALLOWED_ACTIONS:
        raise ValueError(f"Unknown action: {action_name}")

    required_fields = ALLOWED_ACTIONS[action_name]
    missing = required_fields - set(action)

    if missing:
        raise ValueError(
            f"Action '{action_name}' missing required field(s): "
            f"{', '.join(sorted(missing))}"
        )

    for field in required_fields:
        if not isinstance(action[field], str):
            raise ValueError(
                f"Action '{action_name}' field '{field}' must be a string"
            )

    path = action.get("path")
    if path:
        if path.startswith("/"):
            raise ValueError("Absolute paths are not allowed")
        if ".." in path.split("/"):
            raise ValueError("Path traversal is not allowed")
