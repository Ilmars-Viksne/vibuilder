from openai import OpenAI
from providers.base import BaseProvider, ProviderRegistry

@ProviderRegistry.register("lmstudio")
class LMStudioProvider(BaseProvider):
    def __init__(self, model, **kwargs):
        # LM Studio exposes a local OpenAI-compatible server on port 1234
        self.client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio"
        )
        self.model = model

    def chat(self, messages, temperature=0.2):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
