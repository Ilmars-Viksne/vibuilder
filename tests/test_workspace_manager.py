import pytest
from pathlib import Path
from workspace.manager import WorkspaceManager

def test_workspace_resolve_safe(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    # Safe paths
    assert ws.resolve_safe("file.txt") == tmp_path / "file.txt"
    assert ws.resolve_safe("dir/file.txt") == tmp_path / "dir" / "file.txt"
    assert ws.resolve_safe(".") == tmp_path

    # Unsafe paths
    with pytest.raises(ValueError) as excinfo:
        ws.resolve_safe("../outside.txt")
    assert "Path escapes workspace" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        ws.resolve_safe("/etc/passwd")
    assert "Path escapes workspace" in str(excinfo.value)

def test_workspace_operations(tmp_path):
    ws = WorkspaceManager(root=tmp_path)

    ws.create_file("test.txt", "hello")
    assert (tmp_path / "test.txt").read_text() == "hello"

    ws.replace_text("test.txt", "hello", "world")
    assert (tmp_path / "test.txt").read_text() == "world"

    ws.create_folder("subdir")
    assert (tmp_path / "subdir").is_dir()
