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
            "path": "hello.txt",
            "content": "hello",
        }
    )

    assert result["status"] == "ok"
    assert workspace.read_file("hello.txt") == "hello"


def test_executor_replace_text(tmp_path):
    executor, workspace = make_executor(tmp_path)

    executor.execute(
        {
            "action": "create_file",
            "path": "hello.txt",
            "content": "hello",
        }
    )

    result = executor.execute(
        {
            "action": "replace_text",
            "path": "hello.txt",
            "search": "hello",
            "replace": "world",
        }
    )

    assert result["status"] == "ok"
    assert workspace.read_file("hello.txt") == "world"


def test_executor_run_python(tmp_path):
    executor, _ = make_executor(tmp_path)

    executor.execute(
        {
            "action": "create_file",
            "path": "script.py",
            "content": "print('hello from script')\n",
        }
    )

    result = executor.execute(
        {
            "action": "run_python",
            "path": "script.py",
        }
    )

    assert result["status"] == "ok"
    assert result["returncode"] == 0
    assert "hello from script" in result["stdout"]
