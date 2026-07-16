import argparse
import json
import logging

from dotenv import load_dotenv

from agent.architect import Architect
from agent.autonomous import AutonomousAgent
from agent.coder import Coder
from agent.planner import Planner
from agent.reviewer import Reviewer
from agent.tester import Tester
from config.settings import Settings
from memory.manager import MemoryManager
from providers.base import BaseProvider, ProviderRegistry
from providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from tools.executor import ToolExecutor
from tools.git_tools import GitTools
from tools.python_runner import PythonRunner
from tools.test_runner import TestRunner
from workspace.manager import WorkspaceManager

# Import provider modules to trigger registration.
import providers.googleai  # noqa: F401
import providers.lmstudio  # noqa: F401
import providers.mock  # noqa: F401
import providers.nim  # noqa: F401
import providers.ollama  # noqa: F401
import providers.openrouter  # noqa: F401


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            "vibuilder.log",
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger(__name__)

# Module-level exit code constants
EXIT_SUCCESS = 0
EXIT_UNEXPECTED_ERROR = 1
EXIT_FALLBACK_FAILED = 3


def create_provider(
    settings: Settings,
    provider_name: str,
) -> BaseProvider:
    provider_kwargs = settings.get_provider_kwargs(provider_name)

    return ProviderRegistry.create(
        provider_name,
        **provider_kwargs,
    )


def create_agent(
    provider: BaseProvider,
    workspace: WorkspaceManager,
    memory: MemoryManager,
    executor: ToolExecutor,
) -> AutonomousAgent:
    return AutonomousAgent(
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


def print_rate_limit_error(
    exc: ProviderRateLimitError,
) -> None:
    print()
    print(
        "Vibuilder could not complete the task because "
        "the provider is rate-limited."
    )
    print()
    print(f"Provider: {exc.provider}")
    print(f"Model: {exc.model}")

    if exc.retry_after_seconds is not None:
        print(
            "Retry after: approximately "
            f"{exc.retry_after_seconds:g} seconds"
        )

    print()
    print(f"Details: {exc.provider_message}")
    print()
    print("Suggested fixes:")
    print("1. Wait for the retry interval and try again.")
    print("2. Select a non-free model with available quota.")
    print("3. Add provider credits or configure BYOK.")
    print("4. Select another configured provider.")


def validate_provider_selection(
    parser: argparse.ArgumentParser,
    primary_provider: str,
    fallback_provider: str | None,
) -> None:
    available = ProviderRegistry.available()

    if primary_provider not in available:
        parser.error(
            f"Unknown provider: {primary_provider}. "
            f"Available providers: {', '.join(available)}"
        )

    if fallback_provider is None:
        return

    if fallback_provider not in available:
        parser.error(
            f"Unknown fallback provider: {fallback_provider}. "
            f"Available providers: {', '.join(available)}"
        )

    if fallback_provider == primary_provider:
        parser.error(
            "--fallback-provider must differ from "
            "the primary provider"
        )


def create_argument_parser() -> argparse.ArgumentParser:
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
        help=(
            "Override provider, e.g. mock, nim, googleai, "
            "openrouter, ollama, or lmstudio"
        ),
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
            "Provider to use if the primary provider is "
            "rate-limited or temporarily unavailable"
        ),
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default="agent_workspace",
        metavar="PATH",
        help=(
            "Name and location of the agent workspace directory. "
            "Defaults to ./agent_workspace."
        ),
    )
    return parser


def main() -> int:
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.max_steps < 1:
        parser.error("--max-steps must be at least 1")

    settings = Settings()
    primary_name = settings.get_provider_name(args.provider)

    validate_provider_selection(
        parser,
        primary_provider=primary_name,
        fallback_provider=args.fallback_provider,
    )

    workspace = WorkspaceManager(root=args.workspace)
    memory = MemoryManager(
        persist_path=workspace.root / ".vibuilder_memory.json"
    )
    starting_memory_step = memory.current_step

    executor = ToolExecutor(
        workspace=workspace,
        runner=PythonRunner(),
        tests=TestRunner(),
        git=GitTools(workspace.root),
    )

    print(f"Workspace: {workspace.root}")

    try:
        primary_provider = create_provider(
            settings,
            primary_name,
        )
        agent = create_agent(
            provider=primary_provider,
            workspace=workspace,
            memory=memory,
            executor=executor,
        )

        result = agent.run(
            args.goal,
            max_steps=args.max_steps,
        )

    except (
        ProviderRateLimitError,
        ProviderUnavailableError,
    ) as exc:
        logger.warning("%s", exc)

        current_run_has_no_actions = (
            memory.current_step == starting_memory_step
        )

        can_fallback = (
            args.fallback_provider is not None
            and current_run_has_no_actions
        )

        if not can_fallback:
            if isinstance(exc, ProviderRateLimitError):
                print_rate_limit_error(exc)
            else:
                print()
                print("The selected provider is unavailable.")
                print(str(exc))

            if (
                args.fallback_provider is not None
                and memory.current_step > starting_memory_step
            ):
                print()
                print(
                    "Automatic fallback was not attempted "
                    "because workspace actions had already "
                    "been executed."
                )

            return exc.exit_code

        logger.info(
            "Primary provider %s failed before any actions; "
            "trying fallback provider %s",
            primary_name,
            args.fallback_provider,
        )

        print()
        print(
            f"Primary provider '{primary_name}' failed. "
            f"Trying fallback provider "
            f"'{args.fallback_provider}'."
        )

        try:
            fallback_provider = create_provider(
                settings,
                args.fallback_provider,
            )
            fallback_agent = create_agent(
                provider=fallback_provider,
                workspace=workspace,
                memory=memory,
                executor=executor,
            )
            result = fallback_agent.run(
                args.goal,
                max_steps=args.max_steps,
            )

        except ProviderRateLimitError as fallback_exc:
            logger.warning(
                "Fallback provider was rate-limited: %s",
                fallback_exc,
            )
            print_rate_limit_error(fallback_exc)
            return fallback_exc.exit_code

        except ProviderAuthenticationError as fallback_exc:
            logger.error(
                "Fallback provider authentication failed: %s",
                fallback_exc,
            )
            print()
            print("Fallback provider authentication failed.")
            print(str(fallback_exc))
            return fallback_exc.exit_code

        except ProviderUnavailableError as fallback_exc:
            logger.warning(
                "Fallback provider was unavailable: %s",
                fallback_exc,
            )
            print()
            print("The fallback provider is unavailable.")
            print(str(fallback_exc))
            return fallback_exc.exit_code

        except (ValueError, RuntimeError) as fallback_exc:
            logger.exception(
                "Fallback provider creation or execution failed"
            )
            print()
            print("The fallback provider could not complete the task.")
            print(f"Error: {fallback_exc}")
            return EXIT_FALLBACK_FAILED

        except Exception as fallback_exc:
            logger.exception(
                "Unexpected fallback provider failure"
            )
            print()
            print(
                "An unexpected error occurred while using "
                "the fallback provider."
            )
            print(f"Error: {fallback_exc}")
            return EXIT_FALLBACK_FAILED

    except ProviderAuthenticationError as exc:
        logger.error("%s", exc)

        print()
        print(
            "Vibuilder could not authenticate with "
            "the selected provider."
        )
        print(str(exc))
        print()
        print(
            "Check the corresponding API key in "
            "your local .env file."
        )

        return exc.exit_code

    except Exception as exc:
        logger.exception("Vibuilder run failed")

        print()
        print("Vibuilder encountered an unexpected error.")
        print(f"Error: {exc}")
        print()
        print("See vibuilder.log for the full traceback.")

        return EXIT_UNEXPECTED_ERROR

    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
