from __future__ import annotations


class ProviderError(Exception):
    """Base exception for expected LLM provider failures."""

    exit_code = 10


class ProviderRateLimitError(ProviderError):
    """Raised when an LLM provider rejects a request due to rate limiting."""

    exit_code = 11

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        message: str,
        retry_after_seconds: float | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.provider_message = message
        self.retry_after_seconds = retry_after_seconds

        retry_text = ""
        if retry_after_seconds is not None:
            retry_text = f" Retry after approximately {retry_after_seconds:g} seconds."

        super().__init__(
            f"{provider} rate limit reached for model {model!r}. "
            f"{message}{retry_text}"
        )


class ProviderAuthenticationError(ProviderError):
    """Raised when a provider rejects an API key."""

    exit_code = 12

    def __init__(self, *, provider: str, message: str) -> None:
        self.provider = provider
        super().__init__(f"{provider} authentication failed. {message}")


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is temporarily unavailable."""

    exit_code = 13

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        message: str,
    ) -> None:
        self.provider = provider
        self.model = model
        super().__init__(
            f"{provider} is unavailable for model {model!r}. {message}"
        )
