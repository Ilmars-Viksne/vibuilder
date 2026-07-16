import sys
from pathlib import Path
import pytest

from workspace.manager import WorkspaceManager
from memory.manager import MemoryManager
from main import create_argument_parser, main


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


def test_workspace_rejects_nested_traversal(tmp_path):
    workspace = WorkspaceManager(root=tmp_path)

    with pytest.raises(ValueError):
        workspace.resolve("src/../../outside.txt")


def test_workspace_rejects_absolute_action_path(tmp_path):
    workspace = WorkspaceManager(root=tmp_path)

    with pytest.raises(ValueError):
        workspace.resolve((tmp_path / "absolute.py").resolve())


def test_cli_accepts_custom_workspace(monkeypatch, tmp_path):
    selected_workspace = tmp_path / "custom-project"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--goal",
            "Create a hello script",
            "--provider",
            "mock",
            "--workspace",
            str(selected_workspace),
            "--max-steps",
            "5",
        ],
    )

    main()

    assert selected_workspace.is_dir()
    assert (selected_workspace / ".vibuilder_memory.json").exists()


def test_memory_is_stored_in_selected_workspace(tmp_path):
    selected_workspace = tmp_path / "project-alpha"

    workspace = WorkspaceManager(root=selected_workspace)

    memory = MemoryManager(
        persist_path=(workspace.root / ".vibuilder_memory.json")
    )

    assert memory.persist_path == (
        selected_workspace.resolve() / ".vibuilder_memory.json"
    )


def test_workspace_expands_user_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    workspace = WorkspaceManager(root="~/vibuilder-project")

    assert workspace.root == (tmp_path / "vibuilder-project").resolve()


def test_workspace_rejects_existing_file(tmp_path):
    target = tmp_path / "not-a-directory"
    target.write_text("content", encoding="utf-8")

    with pytest.raises(ValueError, match="not a directory|Unable to create"):
        WorkspaceManager(root=target)


def test_workspace_argument_defaults_to_agent_workspace():
    parser = create_argument_parser()

    args = parser.parse_args(
        [
            "--goal",
            "Create a hello script",
        ]
    )

    assert args.workspace == "agent_workspace"


def test_workspace_argument_accepts_custom_path(tmp_path):
    parser = create_argument_parser()
    selected = tmp_path / "project-alpha"

    args = parser.parse_args(
        [
            "--goal",
            "Create a hello script",
            "--workspace",
            str(selected),
        ]
    )

    assert args.workspace == str(selected)
