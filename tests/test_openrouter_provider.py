from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from openai import RateLimitError

from providers.errors import ProviderRateLimitError
from providers.openrouter import OpenRouterProvider


def test_openrouter_translates_rate_limit():
    provider = OpenRouterProvider(
        api_key="test-key",
        model="example/model:free",
    )

    request = httpx.Request(
        "POST",
        "https://openrouter.ai/api/v1/chat/completions",
    )

    response = httpx.Response(
        status_code=429,
        headers={"Retry-After": "30"},
        json={
            "error": {
                "message": "Provider returned error",
                "metadata": {
                    "raw": "Model is temporarily rate-limited",
                    "retry_after_seconds": 30,
                },
            }
        },
        request=request,
    )

    original_error = RateLimitError(
        "Rate limited",
        response=response,
        body=response.json(),
    )

    completion_create = Mock(side_effect=original_error)
    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=completion_create,
            )
        )
    )

    with pytest.raises(ProviderRateLimitError) as exc_info:
        provider.chat(
            [{"role": "user", "content": "Hello"}]
        )

    error = exc_info.value

    assert error.provider == "OpenRouter"
    assert error.model == "example/model:free"
    assert error.retry_after_seconds == 30
    assert "temporarily rate-limited" in error.provider_message
