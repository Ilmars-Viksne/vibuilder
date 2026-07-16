from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from openai import RateLimitError, InternalServerError

from providers.errors import ProviderRateLimitError, ProviderUnavailableError
from providers.nim import NIMProvider


def test_nim_translates_rate_limit():
    provider = NIMProvider(
        api_key="test-key",
        model="test/model",
    )

    request = httpx.Request(
        "POST",
        "https://integrate.api.nvidia.com/v1/chat/completions",
    )
    response = httpx.Response(
        status_code=429,
        headers={"Retry-After": "30"},
        json={
            "error": {
                "message": "Rate limit reached",
            }
        },
        request=request,
    )

    sdk_error = RateLimitError(
        "Rate limit reached",
        response=response,
        body=response.json(),
    )

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=Mock(side_effect=sdk_error),
            )
        )
    )

    with pytest.raises(ProviderRateLimitError) as exc_info:
        provider.chat(
            [{"role": "user", "content": "Hello"}]
        )

    error = exc_info.value

    assert error.provider == "NVIDIA NIM"
    assert error.model == "test/model"
    assert error.retry_after_seconds == 30


def test_nim_translates_service_unavailable():
    provider = NIMProvider(
        api_key="test-key",
        model="test/model",
    )

    request = httpx.Request(
        "POST",
        "https://integrate.api.nvidia.com/v1/chat/completions",
    )
    response = httpx.Response(
        status_code=503,
        json={
            "error": {
                "message": "Service unavailable",
            }
        },
        request=request,
    )

    sdk_error = InternalServerError(
        "Service unavailable",
        response=response,
        body=response.json(),
    )

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=Mock(side_effect=sdk_error),
            )
        )
    )

    with pytest.raises(ProviderUnavailableError):
        provider.chat(
            [{"role": "user", "content": "Hello"}]
        )
