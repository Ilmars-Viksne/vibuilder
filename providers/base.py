from abc import ABC, abstractmethod
from typing import Any, Type


class ProviderRegistry:
    _registry: dict[str, Type["BaseProvider"]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(provider_cls: Type["BaseProvider"]):
            cls._registry[name] = provider_cls
            return provider_cls

        return decorator

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> "BaseProvider":
        if name not in cls._registry:
            available = ", ".join(sorted(cls._registry))
            raise ValueError(
                f"Provider '{name}' not found. "
                f"Available providers: {available}"
            )

        return cls._registry[name](**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._registry)


class BaseProvider(ABC):
    def __init__(self, model: str, **kwargs: Any):
        self.model = model

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        raise NotImplementedError
