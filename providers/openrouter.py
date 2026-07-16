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


@ProviderRegistry.register("openrouter")
class OpenRouterProvider(BaseProvider):
    PROVIDER_NAME = "OpenRouter"

    def __init__(self, api_key: str, model: str, **kwargs: Any) -> None:
        super().__init__(model=model)

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=120.0,
            max_retries=1,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )

        except RateLimitError as exc:
            raise self._create_rate_limit_error(exc) from exc

        except AuthenticationError as exc:
            raise ProviderAuthenticationError(
                provider=self.PROVIDER_NAME,
                message=self._extract_message(exc),
            ) from exc

        except APIConnectionError as exc:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=f"Could not connect to the provider: {exc}",
            ) from exc

        except APIStatusError as exc:
            if exc.status_code == 429:
                raise self._create_rate_limit_error(exc) from exc

            if exc.status_code in {500, 502, 503, 504}:
                raise ProviderUnavailableError(
                    provider=self.PROVIDER_NAME,
                    model=self.model,
                    message=self._extract_message(exc),
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

    def _create_rate_limit_error(
        self,
        exc: Exception,
    ) -> ProviderRateLimitError:
        return ProviderRateLimitError(
            provider=self.PROVIDER_NAME,
            model=self.model,
            message=self._extract_message(exc),
            retry_after_seconds=self._extract_retry_after(exc),
        )

    @staticmethod
    def _extract_retry_after(exc: Exception) -> float | None:
        response = getattr(exc, "response", None)
        if response is None:
            return None

        header_value = response.headers.get("Retry-After")
        if header_value:
            try:
                return float(header_value)
            except (TypeError, ValueError):
                pass

        try:
            body = response.json()
        except Exception:
            return None

        metadata = body.get("error", {}).get("metadata", {})
        value = metadata.get("retry_after_seconds")

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_message(exc: Exception) -> str:
        response = getattr(exc, "response", None)
        if response is None:
            return str(exc)

        try:
            body = response.json()
        except Exception:
            return str(exc)

        error = body.get("error", {})
        metadata = error.get("metadata", {})

        return str(
            metadata.get("raw")
            or error.get("message")
            or str(exc)
        )
