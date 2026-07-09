import pytest

from agent.validation import validate_action


def test_valid_create_file_action():
    validate_action(
        {
            "action": "create_file",
            "path": "hello.py",
            "content": "print('hello')",
        }
    )


def test_unknown_action_rejected():
    with pytest.raises(ValueError):
        validate_action({"action": "delete_everything"})


def test_missing_field_rejected():
    with pytest.raises(ValueError):
        validate_action({"action": "create_file", "path": "hello.py"})


def test_absolute_path_rejected():
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "create_file",
                "path": "/tmp/evil.py",
                "content": "",
            }
        )


def test_path_traversal_rejected():
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "create_file",
                "path": "../evil.py",
                "content": "",
            }
        )
