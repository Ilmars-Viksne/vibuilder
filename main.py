import os
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vibuilder.log")
    ]
)
logger = logging.getLogger(__name__)

from config.settings import Settings
from providers.base import ProviderRegistry

# Import to trigger registry decorators
import providers.nim
import providers.openrouter
import providers.ollama
import providers.lmstudio
import providers.mock

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

def main():
    parser = argparse.ArgumentParser(description="Vibuilder: Autonomous Coding Agent")
    parser.add_argument("--goal", type=str, required=True, help="The task for the agent to complete")
    parser.add_argument("--provider", type=str, help="Override provider (e.g., mock, nim, ollama)")
    args = parser.parse_args()

    settings = Settings()

    try:
        provider_name = settings.resolve_provider(cli_provider=args.provider)
        provider_kwargs = settings.get_provider_kwargs(provider_name)

        # Instantiate provider via Registry
        provider = ProviderRegistry.create(provider_name, **provider_kwargs)
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return

    logger.info(f"Initialized Agent using Provider: {provider_name} | Model: {provider.model}")

    workspace = WorkspaceManager()
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
        memory=MemoryManager(),
        planner=Planner(),
        architect=Architect(),
        coder=Coder(),
        reviewer=Reviewer(),
        tester=Tester()
    )

    agent.run(args.goal)

if __name__ == "__main__":
    main()
