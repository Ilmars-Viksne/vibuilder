import sys
from unittest.mock import MagicMock, patch

import pytest

from providers.base import ProviderRegistry
from providers.errors import ProviderRateLimitError, ProviderUnavailableError
from main import main, create_provider


def test_cli_identical_primary_and_fallback(monkeypatch, tmp_path):
    # Mock settings to return 'mock' as primary provider
    mock_settings = MagicMock()
    mock_settings.get_provider_name.return_value = "mock"

    monkeypatch.setattr("main.Settings", lambda *args, **kwargs: mock_settings)

    test_args = [
        "main.py",
        "--goal", "test goal",
        "--provider", "mock",
        "--fallback-provider", "mock"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2  # argparse error code


def test_cli_unknown_fallback_provider(monkeypatch, tmp_path):
    mock_settings = MagicMock()
    mock_settings.get_provider_name.return_value = "mock"

    monkeypatch.setattr("main.Settings", lambda *args, **kwargs: mock_settings)

    test_args = [
        "main.py",
        "--goal", "test goal",
        "--provider", "mock",
        "--fallback-provider", "non-existent-provider"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2  # argparse error code


@patch("main.AutonomousAgent")
@patch("main.create_provider")
def test_fallback_triggered_when_step_is_0(
    mock_create_provider,
    mock_autonomous_agent,
    monkeypatch,
    tmp_path
):
    # Primary provider setup
    primary_provider = MagicMock()
    mock_create_provider.return_value = primary_provider

    # First agent configuration
    primary_agent = MagicMock()
    # Mock primary agent run to raise a rate limit exception
    primary_agent.run.side_effect = ProviderRateLimitError(
        provider="MockPrimary",
        model="primary-model",
        message="Rate limited",
        retry_after_seconds=5
    )

    # Setup mock AutonomousAgent behavior. First instantiation returns primary, second returns fallback.
    fallback_agent = MagicMock()
    fallback_agent.run.return_value = {"finished": True, "result": "success"}

    mock_autonomous_agent.side_effect = [primary_agent, fallback_agent]

    # Mock MemoryManager current_step to be 0
    mock_memory = MagicMock()
    mock_memory.current_step = 0
    monkeypatch.setattr("main.MemoryManager", lambda *args, **kwargs: mock_memory)

    # Settings and arguments
    mock_settings = MagicMock()
    mock_settings.get_provider_name.return_value = "mock"
    monkeypatch.setattr("main.Settings", lambda *args, **kwargs: mock_settings)

    test_args = [
        "main.py",
        "--goal", "test goal",
        "--provider", "mock",
        "--fallback-provider", "nim"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    # Check that fallback agent was run
    fallback_agent.run.assert_called_once_with("test goal", max_steps=50)


@patch("main.AutonomousAgent")
@patch("main.create_provider")
def test_no_fallback_when_step_greater_than_0(
    mock_create_provider,
    mock_autonomous_agent,
    monkeypatch,
    tmp_path
):
    # Primary provider setup
    primary_provider = MagicMock()
    mock_create_provider.return_value = primary_provider

    # First agent configuration
    primary_agent = MagicMock()
    # Mock primary agent run to raise a rate limit exception
    primary_agent.run.side_effect = ProviderRateLimitError(
        provider="MockPrimary",
        model="primary-model",
        message="Rate limited",
        retry_after_seconds=5
    )

    mock_autonomous_agent.return_value = primary_agent

    # Mock MemoryManager current_step to be greater than 0 (e.g., 2)
    mock_memory = MagicMock()
    mock_memory.current_step = 2
    monkeypatch.setattr("main.MemoryManager", lambda *args, **kwargs: mock_memory)

    # Settings and arguments
    mock_settings = MagicMock()
    mock_settings.get_provider_name.return_value = "mock"
    monkeypatch.setattr("main.Settings", lambda *args, **kwargs: mock_settings)

    test_args = [
        "main.py",
        "--goal", "test goal",
        "--provider", "mock",
        "--fallback-provider", "nim"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        main()

    # Should exit with the exit code of ProviderRateLimitError (11)
    assert exc_info.value.code == 11


@patch("main.AutonomousAgent")
@patch("main.create_provider")
def test_fallback_provider_creation_fails(
    mock_create_provider,
    mock_autonomous_agent,
    monkeypatch,
    tmp_path
):
    # Primary provider setup
    primary_provider = MagicMock()
    # Success on first call (primary creation), but raise error on second call (fallback creation)
    mock_create_provider.side_effect = [
        primary_provider,
        ValueError("Failed to load credentials")
    ]

    # First agent configuration
    primary_agent = MagicMock()
    primary_agent.run.side_effect = ProviderUnavailableError(
        provider="MockPrimary",
        model="primary-model",
        message="Service Unavailable"
    )

    mock_autonomous_agent.return_value = primary_agent

    # Mock MemoryManager current_step to be 0
    mock_memory = MagicMock()
    mock_memory.current_step = 0
    monkeypatch.setattr("main.MemoryManager", lambda *args, **kwargs: mock_memory)

    # Settings and arguments
    mock_settings = MagicMock()
    mock_settings.get_provider_name.return_value = "mock"
    monkeypatch.setattr("main.Settings", lambda *args, **kwargs: mock_settings)

    test_args = [
        "main.py",
        "--goal", "test goal",
        "--provider", "mock",
        "--fallback-provider", "nim"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3


@patch("main.AutonomousAgent")
@patch("main.create_provider")
def test_fallback_provider_run_fails(
    mock_create_provider,
    mock_autonomous_agent,
    monkeypatch,
    tmp_path
):
    # Primary provider setup
    primary_provider = MagicMock()
    mock_create_provider.return_value = primary_provider

    # First agent configuration
    primary_agent = MagicMock()
    primary_agent.run.side_effect = ProviderUnavailableError(
        provider="MockPrimary",
        model="primary-model",
        message="Service Unavailable"
    )

    # Second agent configuration (fallback)
    fallback_agent = MagicMock()
    fallback_agent.run.side_effect = RuntimeError("Internal error in fallback")

    mock_autonomous_agent.side_effect = [primary_agent, fallback_agent]

    # Mock MemoryManager current_step to be 0
    mock_memory = MagicMock()
    mock_memory.current_step = 0
    monkeypatch.setattr("main.MemoryManager", lambda *args, **kwargs: mock_memory)

    # Settings and arguments
    mock_settings = MagicMock()
    mock_settings.get_provider_name.return_value = "mock"
    monkeypatch.setattr("main.Settings", lambda *args, **kwargs: mock_settings)

    test_args = [
        "main.py",
        "--goal", "test goal",
        "--provider", "mock",
        "--fallback-provider", "nim"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3
