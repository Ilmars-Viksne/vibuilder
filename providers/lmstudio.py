from __future__ import annotations

from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from providers.base import BaseProvider, ProviderRegistry
from providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


@ProviderRegistry.register("lmstudio")
class LMStudioProvider(BaseProvider):
    PROVIDER_NAME = "LM Studio"

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:1234/v1",
        api_key: str = "lm-studio",
        **kwargs: Any,
    ):
        super().__init__(model=model)
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )

        except RateLimitError as exc:
            raise ProviderRateLimitError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=str(exc),
                retry_after_seconds=self._extract_retry_after(exc),
            ) from exc

        except AuthenticationError as exc:
            raise ProviderAuthenticationError(
                provider=self.PROVIDER_NAME,
                message=str(exc),
            ) from exc

        except APIConnectionError as exc:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=f"Could not connect to LM Studio: {exc}",
            ) from exc

        except APIStatusError as exc:
            if exc.status_code == 429:
                raise ProviderRateLimitError(
                    provider=self.PROVIDER_NAME,
                    model=self.model,
                    message=str(exc),
                    retry_after_seconds=self._extract_retry_after(exc),
                ) from exc

            if exc.status_code in {500, 502, 503, 504}:
                raise ProviderUnavailableError(
                    provider=self.PROVIDER_NAME,
                    model=self.model,
                    message=str(exc),
                ) from exc

            raise

        content = response.choices[0].message.content
        if not content:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message="The provider returned an empty response.",
            )

        return content

    @staticmethod
    def _extract_retry_after(exc: Exception) -> float | None:
        response = getattr(exc, "response", None)
        if response is None:
            return None

        value = response.headers.get("Retry-After")
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
