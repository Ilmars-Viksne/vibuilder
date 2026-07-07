import requests
from providers.base import BaseProvider, ProviderRegistry

@ProviderRegistry.register("ollama")
class OllamaProvider(BaseProvider):
    def __init__(self, model, **kwargs):
        self.model = model

    def chat(self, messages, temperature=0.2):
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature}
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
