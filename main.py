import argparse
import json
import logging
import sys

from dotenv import load_dotenv

from config.settings import Settings
from providers.base import BaseProvider, ProviderRegistry

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

from providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)

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


def create_provider(
    settings: Settings,
    provider_name: str,
) -> BaseProvider:
    provider_kwargs = settings.get_provider_kwargs(provider_name)
    return ProviderRegistry.create(
        provider_name,
        **provider_kwargs,
    )


def print_rate_limit_error(exc: ProviderRateLimitError) -> None:
    print()
    print("Vibuilder could not complete the task because the provider is rate-limited.")
    print()
    print(f"Provider: {exc.provider}")
    print(f"Model: {exc.model}")

    if exc.retry_after_seconds is not None:
        print(f"Retry after: approximately {exc.retry_after_seconds:g} seconds")

    print()
    print(f"Details: {exc.provider_message}")
    print()
    print("Suggested fixes:")
    print("1. Wait for the indicated interval and try again.")
    print("2. Select a non-free model with available quota.")
    print("3. Add credits or configure BYOK for the provider.")
    print("4. Select another configured provider, for example:")
    print("   python main.py --goal $goal --provider nim --max-steps 30")


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
    parser.add_argument(
        "--fallback-provider",
        type=str,
        default=None,
        help=(
            "Provider to use if the primary provider is rate-limited "
            "or temporarily unavailable, for example: nim"
        ),
    )
    args = parser.parse_args()

    settings = Settings()
    provider_name = settings.get_provider_name(args.provider)

    if (
        args.fallback_provider
        and args.fallback_provider == provider_name
    ):
        parser.error(
            "--fallback-provider must differ from the primary provider"
        )

    if (
        args.fallback_provider
        and args.fallback_provider not in ProviderRegistry.available()
    ):
        parser.error(
            f"Unknown fallback provider: {args.fallback_provider}"
        )

    provider = create_provider(settings, provider_name)

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

    try:
        result = agent.run(args.goal, max_steps=args.max_steps)
        print(json.dumps(result, indent=2))

    except (ProviderRateLimitError, ProviderUnavailableError) as exc:
        if args.fallback_provider and memory.current_step == 0:
            logger.warning(
                "Primary provider failed before executing actions; "
                "trying fallback provider %s",
                args.fallback_provider,
            )

            try:
                fallback_provider = create_provider(
                    settings,
                    args.fallback_provider,
                )
            except Exception as creation_exc:
                logger.exception("Fallback provider creation failed")
                print()
                print("Failed to initialize the fallback provider.")
                print(f"Error: {creation_exc}")
                raise SystemExit(3)

            fallback_agent = AutonomousAgent(
                provider=fallback_provider,
                workspace=workspace,
                executor=executor,
                memory=memory,
                planner=Planner(),
                architect=Architect(),
                coder=Coder(),
                reviewer=Reviewer(),
                tester=Tester(),
            )

            try:
                result = fallback_agent.run(
                    args.goal,
                    max_steps=args.max_steps,
                )
                print(json.dumps(result, indent=2))
                raise SystemExit(0)
            except Exception as fallback_exc:
                logger.exception("Fallback provider failed")
                print()
                print("The fallback provider also failed.")
                print(f"Error: {fallback_exc}")
                raise SystemExit(3)

        if isinstance(exc, ProviderRateLimitError):
            logger.warning("%s", exc)
            print_rate_limit_error(exc)
        else:
            logger.warning("%s", exc)
            print()
            print("The selected LLM provider is temporarily unavailable.")
            print(str(exc))
            print()
            print("Try again later or select another provider.")

        if memory.current_step > 0:
            print()
            print(
                "Automatic fallback was not attempted because the first "
                "provider had already executed workspace actions."
            )

        raise SystemExit(exc.exit_code)

    except ProviderAuthenticationError as exc:
        logger.error("%s", exc)
        print()
        print("Vibuilder could not authenticate with the selected provider.")
        print(str(exc))
        print()
        print("Check the corresponding API key in your local .env file.")
        raise SystemExit(exc.exit_code)

    except Exception as exc:
        logger.exception("Vibuilder run failed")
        print()
        print("Vibuilder encountered an unexpected error.")
        print(f"Error: {exc}")
        print()
        print("See vibuilder.log for the full traceback.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
