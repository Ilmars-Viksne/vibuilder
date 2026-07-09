import pytest

from workspace.manager import WorkspaceManager


def test_workspace_resolve_safe(tmp_path):
    ws = WorkspaceManager(root=tmp_path)
    resolved = ws.resolve("src/main.py")
    assert resolved == tmp_path.resolve() / "src" / "main.py"


def test_workspace_rejects_absolute_path(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    with pytest.raises(ValueError):
        ws.resolve("/tmp/evil.py")


def test_workspace_rejects_path_traversal(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    with pytest.raises(ValueError):
        ws.resolve("../evil.py")


def test_workspace_operations(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    ws.create_folder("src")
    ws.write_file("src/hello.py", "print('hello')\n")

    assert ws.exists("src")
    assert ws.exists("src/hello.py")
    assert ws.read_file("src/hello.py") == "print('hello')\n"

    ws.replace_text("src/hello.py", "hello", "hi")
    assert ws.read_file("src/hello.py") == "print('hi')\n"
