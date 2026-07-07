from abc import ABC, abstractmethod

class ProviderRegistry:
    _registry = {}

    @classmethod
    def register(cls, name):
        def wrapper(wrapped_class):
            cls._registry[name] = wrapped_class
            return wrapped_class
        return wrapper

    @classmethod
    def create(cls, name, **kwargs):
        if name not in cls._registry:
            raise ValueError(f"Provider '{name}' not found. Available: {list(cls._registry.keys())}")
        return cls._registry[name](**kwargs)

class BaseProvider(ABC):
    @abstractmethod
    def chat(self, messages, temperature=0.2):
        pass
