from openai import OpenAI

from providers.base import BaseProvider, ProviderRegistry


@ProviderRegistry.register("lmstudio")
class LMStudioProvider(BaseProvider):
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:1234/v1",
        api_key: str = "lm-studio",
        **kwargs,
    ):
        super().__init__(model=model)
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
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
