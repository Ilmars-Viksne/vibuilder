from __future__ import annotations

import logging
from typing import Any

from google import genai
from google.genai import types

from providers.base import BaseProvider, ProviderRegistry
from providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)

logger = logging.getLogger(__name__)


@ProviderRegistry.register("googleai")
class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider using the Gemini API."""

    PROVIDER_NAME = "Google AI"

    def __init__(
        self,
        model: str,
        api_key: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model)

        if not api_key or not api_key.strip():
            raise ProviderAuthenticationError(
                provider=self.PROVIDER_NAME,
                message="Google AI API key is missing.",
            )

        self.client = genai.Client(api_key=api_key)

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        """
        Generate a response from Google AI.

        Vibuilder uses OpenAI-style message dictionaries. This method
        converts them into Google Gen AI SDK content objects.
        """
        system_instruction, contents = self._convert_messages(messages)

        config_kwargs: dict[str, Any] = {
            "temperature": temperature,
        }

        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    **config_kwargs
                ),
            )
        except Exception as exc:
            self._raise_provider_error(exc)

        text = getattr(response, "text", None)

        if not text or not text.strip():
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=(
                    "Google AI returned an empty response."
                ),
            )

        return text.strip()

    @staticmethod
    def _convert_messages(
        messages: list[dict[str, str]],
    ) -> tuple[str | None, list[types.Content]]:
        """
        Convert OpenAI-style messages to Google Gen AI contents.

        System messages become a system instruction. User and
        assistant messages retain their conversational roles.
        """
        system_parts: list[str] = []
        contents: list[types.Content] = []

        for message in messages:
            role = message.get("role")
            content = message.get("content", "")

            if not isinstance(content, str):
                raise ValueError(
                    "Google AI message content must be a string."
                )

            if role == "system":
                if content.strip():
                    system_parts.append(content.strip())
                continue

            if role == "user":
                google_role = "user"
            elif role == "assistant":
                google_role = "model"
            else:
                raise ValueError(
                    f"Unsupported message role: {role!r}"
                )

            contents.append(
                types.Content(
                    role=google_role,
                    parts=[
                        types.Part.from_text(text=content)
                    ],
                )
            )

        if not contents:
            raise ValueError(
                "At least one user or assistant message is required."
            )

        system_instruction = (
            "\n\n".join(system_parts)
            if system_parts
            else None
        )

        return system_instruction, contents

    def _raise_provider_error(
        self,
        exc: Exception,
    ) -> None:
        """
        Translate Google SDK errors into Vibuilder provider errors.

        Google SDK exception classes and attributes may vary between
        SDK releases, so status information is read defensively.
        """
        status_code = self._extract_status_code(exc)
        message = str(exc) or exc.__class__.__name__

        logger.error(
            "Google AI request failed for model %s: %s",
            self.model,
            message,
        )

        if status_code in {401, 403}:
            raise ProviderAuthenticationError(
                provider=self.PROVIDER_NAME,
                message=message,
            ) from exc

        if status_code == 429:
            raise ProviderRateLimitError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=message,
            ) from exc

        raise ProviderUnavailableError(
            provider=self.PROVIDER_NAME,
            model=self.model,
            message=message,
        ) from exc

    @staticmethod
    def _extract_status_code(
        exc: Exception,
    ) -> int | None:
        for attribute in (
            "status_code",
            "code",
        ):
            value = getattr(exc, attribute, None)

            if isinstance(value, int):
                return value

            if isinstance(value, str) and value.isdigit():
                return int(value)

        response = getattr(exc, "response", None)

        if response is not None:
            status_code = getattr(
                response,
                "status_code",
                None,
            )

            if isinstance(status_code, int):
                return status_code

        return None
