from abc import ABC, abstractmethod
from typing import Any, Callable, Type


class ProviderRegistry:
    _registry: dict[str, Type["BaseProvider"]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type["BaseProvider"]], Type["BaseProvider"]]:
        if not name or not isinstance(name, str):
            raise ValueError("Provider name must be a non-empty string")

        def decorator(provider_cls: Type["BaseProvider"]) -> Type["BaseProvider"]:
            cls._registry[name] = provider_cls
            return provider_cls

        return decorator

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> "BaseProvider":
        if name not in cls._registry:
            available = ", ".join(sorted(cls._registry)) or "<none>"
            raise ValueError(f"Unknown provider: {name}. Available providers: {available}")
        return cls._registry[name](**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._registry)


class BaseProvider(ABC):
    def __init__(self, model: str, **kwargs: Any):
        self.model = model

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        raise NotImplementedError
