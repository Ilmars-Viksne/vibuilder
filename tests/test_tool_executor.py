from tools.executor import ToolExecutor
from tools.python_runner import PythonRunner
from tools.test_runner import TestRunner
from tools.git_tools import GitTools
from workspace.manager import WorkspaceManager


def make_executor(tmp_path):
    workspace = WorkspaceManager(root=tmp_path)
    return ToolExecutor(
        workspace=workspace,
        runner=PythonRunner(),
        tests=TestRunner(),
        git=GitTools(workspace.root),
    ), workspace


def test_executor_create_file(tmp_path):
    executor, workspace = make_executor(tmp_path)

    result = executor.execute(
        {
            "action": "create_file",
            "path": "hello.py",
            "content": "print('hello')\n",
        }
    )

    assert result["success"] is True
    assert workspace.read_file("hello.py") == "print('hello')\n"


def test_executor_replace_text(tmp_path):
    executor, workspace = make_executor(tmp_path)
    workspace.write_file("hello.txt", "hello world")

    result = executor.execute(
        {
            "action": "replace_text",
            "path": "hello.txt",
            "search": "world",
            "replace": "vibuilder",
        }
    )

    assert result["success"] is True
    assert workspace.read_file("hello.txt") == "hello vibuilder"


def test_executor_run_python(tmp_path):
    executor, _ = make_executor(tmp_path)

    executor.execute(
        {
            "action": "create_file",
            "path": "hello.py",
            "content": "print('hello')\n",
        }
    )

    result = executor.execute(
        {
            "action": "run_python",
            "path": "hello.py",
        }
    )

    assert result["success"] is True
    assert "hello" in result["stdout"]
