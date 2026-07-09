from openai import OpenAI

from providers.base import BaseProvider, ProviderRegistry


@ProviderRegistry.register("openrouter")
class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, **kwargs):
        super().__init__(model=model)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
