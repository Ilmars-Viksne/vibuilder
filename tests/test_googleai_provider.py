from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from providers.googleai import GoogleAIProvider


@patch("providers.googleai.genai.Client")
def test_googleai_generates_response(
    mock_client_class,
):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = (
        SimpleNamespace(text="Hello from Gemma 4")
    )
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        api_key="test-key",
        model="gemma-4-31b-it",
    )

    result = provider.chat(
        [
            {
                "role": "system",
                "content": "You are a coding assistant.",
            },
            {
                "role": "user",
                "content": "Say hello.",
            },
        ],
        temperature=0.2,
    )

    assert result == "Hello from Gemma 4"

    mock_client_class.assert_called_once_with(
        api_key="test-key"
    )
    mock_client.models.generate_content.assert_called_once()


@patch("providers.googleai.genai.Client")
def test_googleai_converts_assistant_role_to_model(
    mock_client_class,
):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = (
        SimpleNamespace(text="Response")
    )
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        api_key="test-key",
        model="gemma-4-31b-it",
    )

    provider.chat(
        [
            {
                "role": "user",
                "content": "First question",
            },
            {
                "role": "assistant",
                "content": "First answer",
            },
            {
                "role": "user",
                "content": "Second question",
            },
        ]
    )

    call = mock_client.models.generate_content.call_args
    contents = call.kwargs["contents"]

    assert contents[0].role == "user"
    assert contents[1].role == "model"
    assert contents[2].role == "user"


@patch("providers.googleai.genai.Client")
def test_googleai_translates_rate_limit(
    mock_client_class,
):
    error = RuntimeError("Rate limit exceeded")
    error.status_code = 429

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = error
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        api_key="test-key",
        model="gemma-4-31b-it",
    )

    with pytest.raises(ProviderRateLimitError):
        provider.chat(
            [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ]
        )


@patch("providers.googleai.genai.Client")
def test_googleai_translates_authentication_error(
    mock_client_class,
):
    error = RuntimeError("Invalid API key")
    error.status_code = 401

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = error
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        api_key="test-key",
        model="gemma-4-31b-it",
    )

    with pytest.raises(ProviderAuthenticationError):
        provider.chat(
            [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ]
        )


@patch("providers.googleai.genai.Client")
def test_googleai_translates_service_error(
    mock_client_class,
):
    error = RuntimeError("Service unavailable")
    error.status_code = 503

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = error
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        api_key="test-key",
        model="gemma-4-31b-it",
    )

    with pytest.raises(ProviderUnavailableError):
        provider.chat(
            [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ]
        )


@patch("providers.googleai.genai.Client")
def test_googleai_rejects_empty_response(
    mock_client_class,
):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = (
        SimpleNamespace(text="")
    )
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        api_key="test-key",
        model="gemma-4-31b-it",
    )

    with pytest.raises(ProviderUnavailableError):
        provider.chat(
            [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ]
        )


def test_googleai_rejects_missing_api_key():
    with pytest.raises(ProviderAuthenticationError) as exc_info:
        GoogleAIProvider(
            api_key="",
            model="gemma-4-31b-it",
        )

    assert exc_info.value.provider == "Google AI"


def test_googleai_rejects_unknown_message_role():
    with patch(
        "providers.googleai.genai.Client"
    ):
        provider = GoogleAIProvider(
            api_key="test-key",
            model="gemma-4-31b-it",
        )

        with pytest.raises(
            ValueError,
            match="Unsupported message role",
        ):
            provider.chat(
                [
                    {
                        "role": "tool",
                        "content": "Tool result",
                    }
                ]
            )


@patch("providers.googleai.genai.Client")
def test_googleai_smoke_test(mock_client_class):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = (
        SimpleNamespace(
            text='{"action": "finish"}'
        )
    )
    mock_client_class.return_value = mock_client

    provider = GoogleAIProvider(
        model="gemma-4-31b-it",
        api_key="test-key",
    )

    result = provider.chat(
        [
            {
                "role": "system",
                "content": (
                    "Return one valid JSON action."
                ),
            },
            {
                "role": "user",
                "content": "Finish the task.",
            },
        ]
    )

    assert result == '{"action": "finish"}'
    mock_client.models.generate_content.assert_called_once()


@pytest.mark.integration
def test_googleai_live_smoke():
    api_key = os.getenv("GOOGLE_AI_API_KEY")

    if not api_key:
        pytest.skip(
            "GOOGLE_AI_API_KEY is not configured"
        )

    provider = GoogleAIProvider(
        model="gemma-4-31b-it",
        api_key=api_key,
    )

    response = provider.chat(
        [
            {
                "role": "user",
                "content": "Reply with exactly: OK",
            }
        ],
        temperature=0.0,
    )

    assert response
