from openai import OpenAI
from providers.base import BaseProvider, ProviderRegistry

@ProviderRegistry.register("openrouter")
class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key, model):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model

    def chat(self, messages, temperature=0.2):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
