from agent.architect import Architect
from agent.autonomous import AutonomousAgent
from agent.coder import Coder
from agent.planner import Planner
from agent.reviewer import Reviewer
from agent.tester import Tester
from memory.manager import MemoryManager
from providers.mock import MockProvider
from tools.executor import ToolExecutor
from tools.git_tools import GitTools
from tools.python_runner import PythonRunner
from tools.test_runner import TestRunner
from workspace.manager import WorkspaceManager


def test_autonomous_mock_run(tmp_path):
    workspace = WorkspaceManager(root=tmp_path)
    memory = MemoryManager(persist_path=tmp_path / ".memory.json")
    provider = MockProvider()

    executor = ToolExecutor(
        workspace=workspace,
        runner=PythonRunner(),
        tests=TestRunner(),
        git=GitTools(workspace.root),
    )

    agent = AutonomousAgent(
        provider=provider,
        workspace=workspace,
        executor=executor,
        memory=memory,
        planner=Planner(),
        architect=Architect(),
        coder=Coder(),
        reviewer=Reviewer(),
        tester=Tester(),
    )

    result = agent.run(
        "Create a hello module and tests",
        max_steps=10,
    )

    assert (tmp_path / "hello.py").exists()
    assert (tmp_path / "test_hello.py").exists()
    assert result["last_action"]["action"] == "finish"
    assert "Mock review" in result["review"]

    test_events = [
        event
        for event in result["history"]
        if event["action"].get("action") == "run_tests"
    ]

    assert test_events
    assert test_events[-1]["result"]["status"] == "ok"
    assert test_events[-1]["result"]["returncode"] == 0
