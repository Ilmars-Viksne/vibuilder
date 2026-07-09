import requests

from providers.base import BaseProvider, ProviderRegistry


@ProviderRegistry.register("ollama")
class OllamaProvider(BaseProvider):
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        super().__init__(model=model)
        self.base_url = base_url.rstrip("/")

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")
