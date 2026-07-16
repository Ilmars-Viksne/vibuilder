from __future__ import annotations

import requests

from providers.base import BaseProvider, ProviderRegistry
from providers.errors import ProviderUnavailableError


@ProviderRegistry.register("ollama")
class OllamaProvider(BaseProvider):
    PROVIDER_NAME = "Ollama"

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        super().__init__(model=model)
        self.base_url = base_url.rstrip("/")

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()

        except requests.Timeout as exc:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message="The local Ollama request timed out.",
            ) from exc

        except requests.ConnectionError as exc:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=(
                    f"Could not connect to Ollama at {self.base_url}. "
                    "Confirm that the Ollama service is running."
                ),
            ) from exc

        except requests.HTTPError as exc:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=f"Ollama returned an HTTP error: {exc}",
            ) from exc

        try:
            data = response.json()
        except Exception as exc:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message=f"Failed to parse JSON response from Ollama: {exc}",
            ) from exc

        content = data.get("message", {}).get("content")

        if not content:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                model=self.model,
                message="Ollama returned an empty response.",
            )

        return content
