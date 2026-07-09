import argparse
import json
import logging

from dotenv import load_dotenv

from config.settings import Settings
from providers.base import ProviderRegistry

# Import providers to trigger registry decorators.
import providers.nim  # noqa: F401
import providers.openrouter  # noqa: F401
import providers.ollama  # noqa: F401
import providers.lmstudio  # noqa: F401
import providers.mock  # noqa: F401

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
from agent.autonomous import AutonomousAgent


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vibuilder.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Vibuilder: Autonomous Coding Agent"
    )
    parser.add_argument(
        "--goal",
        type=str,
        required=True,
        help="The task for the agent to complete",
    )
    parser.add_argument(
        "--provider",
        type=str,
        help="Override provider, e.g. mock, nim, ollama",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum autonomous execution steps",
    )
    args = parser.parse_args()

    settings = Settings()
    provider_name = settings.get_provider_name(args.provider)
    provider_kwargs = settings.get_provider_kwargs(provider_name)
    provider = ProviderRegistry.create(provider_name, **provider_kwargs)

    workspace = WorkspaceManager()
    memory = MemoryManager()
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

    result = agent.run(args.goal, max_steps=args.max_steps)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
