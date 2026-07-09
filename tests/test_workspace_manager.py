import pytest

from workspace.manager import WorkspaceManager


def test_workspace_resolve_safe(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    resolved = ws.resolve("folder/file.txt")

    assert resolved.parent.name == "folder"
    assert resolved.name == "file.txt"


def test_workspace_rejects_absolute_path(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    with pytest.raises(ValueError):
        ws.resolve("/tmp/outside.txt")


def test_workspace_rejects_path_traversal(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    with pytest.raises(ValueError):
        ws.resolve("../outside.txt")


def test_workspace_operations(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    ws.create_folder("src")
    ws.create_file("src/app.py", "print('hello')\n")

    assert ws.read_file("src/app.py") == "print('hello')\n"

    ws.replace_text("src/app.py", "hello", "world")

    assert ws.read_file("src/app.py") == "print('world')\n"

    ws.write_file("src/app.py", "print('edited')\n")

    assert ws.read_file("src/app.py") == "print('edited')\n"
