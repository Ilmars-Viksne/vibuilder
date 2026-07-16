from providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


def test_rate_limit_error_preserves_context():
    error = ProviderRateLimitError(
        provider="OpenRouter",
        model="example/model:free",
        message="Temporarily rate-limited",
        retry_after_seconds=30,
    )

    assert error.provider == "OpenRouter"
    assert error.model == "example/model:free"
    assert error.retry_after_seconds == 30
    assert error.exit_code == 11
    assert "Temporarily rate-limited" in str(error)


def test_authentication_error():
    error = ProviderAuthenticationError(
        provider="OpenRouter",
        message="Invalid API key",
    )

    assert error.provider == "OpenRouter"
    assert error.exit_code == 12
    assert "Invalid API key" in str(error)


def test_unavailable_error():
    error = ProviderUnavailableError(
        provider="NVIDIA NIM",
        model="example/model",
        message="Service unavailable",
    )

    assert error.provider == "NVIDIA NIM"
    assert error.model == "example/model"
    assert error.exit_code == 13
