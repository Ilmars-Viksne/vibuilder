from openai import OpenAI
from providers.base import BaseProvider, ProviderRegistry

@ProviderRegistry.register("nim")
class NIMProvider(BaseProvider):
    def __init__(self, api_key, model):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        self.model = model

    def chat(self, messages, temperature=0.2):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
