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


def test_unexpected_field_rejected():
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "finish",
                "path": "unexpected.txt",
            }
        )


def test_valid_list_directory_action():
    validate_action(
        {
            "action": "list_directory",
            "path": ".",
        }
    )


def test_valid_read_file_action():
    validate_action(
        {
            "action": "read_file",
            "path": "calculator.py",
        }
    )


def test_read_file_absolute_path_rejected():
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "read_file",
                "path": "C:/outside.txt",
            }
        )


def test_read_file_traversal_rejected():
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "read_file",
                "path": "../outside.txt",
            }
        )


def test_run_python_rejects_shell_command():
    with pytest.raises(
        ValueError,
        match=r"\.py",
    ):
        validate_action(
            {
                "action": "run_python",
                "path": "ls -R",
            }
        )


@pytest.mark.parametrize(
    "path",
    [
        "/tmp/outside.py",
        r"C:\outside.py",
        "C:/outside.py",
        r"C:outside.py",
        r"\\server\share\outside.py",
    ],
)
def test_absolute_paths_rejected(path):
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "read_file",
                "path": path,
            }
        )


@pytest.mark.parametrize(
    "path",
    [
        "../outside.py",
        "src/../../outside.py",
        r"..\outside.py",
        r"src\..\..\outside.py",
    ],
)
def test_traversal_paths_rejected(path):
    with pytest.raises(ValueError):
        validate_action(
            {
                "action": "read_file",
                "path": path,
            }
        )


def test_list_directory_accepts_dot_path():
    validate_action(
        {
            "action": "list_directory",
            "path": ".",
        }
    )
