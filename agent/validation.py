from pathlib import PurePosixPath, PureWindowsPath


ALLOWED_ACTIONS = {
    "create_folder": {"path"},
    "create_file": {"path", "content"},
    "edit_file": {"path", "content"},
    "replace_text": {"path", "search", "replace"},
    "list_directory": {"path"},
    "read_file": {"path"},
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

    if action_name == "run_python":
        path = PurePosixPath(action["path"])
        if path.suffix.lower() != ".py":
            raise ValueError("run_python path must end with .py")

    unexpected = set(action) - required_fields - {"action"}
    if unexpected:
        raise ValueError(
            f"Action '{action_name}' contains unexpected fields: "
            f"{', '.join(sorted(unexpected))}"
        )


def _validate_relative_safe_path(path: str) -> None:
    if not isinstance(path, str):
        raise ValueError("Path must be a string")

    if not path.strip():
        raise ValueError("Path must not be empty")

    posix_path = PurePosixPath(path)
    windows_path = PureWindowsPath(path)

    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
    ):
        raise ValueError("Absolute paths are not allowed")

    if (
        ".." in posix_path.parts
        or ".." in windows_path.parts
    ):
        raise ValueError("Path traversal is not allowed")
