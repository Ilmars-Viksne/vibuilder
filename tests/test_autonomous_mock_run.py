import pytest
from agent.autonomous import AutonomousAgent
from providers.mock import MockProvider
from workspace.manager import WorkspaceManager
from memory.manager import MemoryManager
from tools.executor import ToolExecutor
from tools.python_runner import PythonRunner
from tools.test_runner import TestRunner
from tools.git_tools import GitTools
from agent.planner import Planner
from agent.architect import Architect
from agent.coder import Coder
from agent.reviewer import Reviewer
from agent.tester import Tester

def test_autonomous_mock_run(tmp_path):
    workspace = WorkspaceManager(root=tmp_path)
    memory = MemoryManager(persist_path=tmp_path / ".memory.json")
    provider = MockProvider()

    executor = ToolExecutor(
        workspace,
        PythonRunner(),
        TestRunner(),
        GitTools(workspace.root)
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
        tester=Tester()
    )

    result = agent.run("Test goal", max_steps=5)

    assert result["steps_taken"] > 0
    assert (tmp_path / "test.py").exists()
    assert "Mock working" in (tmp_path / "test.py").read_text()

    # Check memory
    assert len(memory.history) > 0
    assert memory.history[0]["phase"] == "execute"
