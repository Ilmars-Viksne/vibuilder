import os
from pathlib import Path
from typing import Any

import yaml


class Settings:
    def __init__(self, config_path: str | Path = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if "providers" not in data:
            raise ValueError("Config must contain a top-level 'providers' section")

        return data

    def resolve_provider(self, cli_provider: str | None = None) -> str:
        """
        Provider resolution priority:
        1. CLI --provider
        2. DEFAULT_PROVIDER environment variable
        3. config.yaml provider
        """
        provider = (
            cli_provider
            or os.getenv("DEFAULT_PROVIDER")
            or self.config.get("provider")
        )

        if not provider:
            raise ValueError("No provider configured")

        providers = self.config.get("providers", {})
        if provider not in providers:
            available = ", ".join(sorted(providers))
            raise ValueError(
                f"Provider '{provider}' not found in config. "
                f"Available providers: {available}"
            )

        return provider

    def get_provider_kwargs(self, provider_name: str) -> dict[str, Any]:
        providers = self.config.get("providers", {})
        if provider_name not in providers:
            raise ValueError(f"Provider '{provider_name}' not found in config")

        provider_config = dict(providers[provider_name])
        kwargs: dict[str, Any] = {}

        if "model" in provider_config:
            kwargs["model"] = provider_config["model"]

        if "base_url" in provider_config:
            kwargs["base_url"] = provider_config["base_url"]

        if "api_key" in provider_config:
            kwargs["api_key"] = provider_config["api_key"]

        api_key_env = provider_config.get("api_key_env")
        if api_key_env:
            api_key = os.getenv(api_key_env)
            if not api_key:
                raise ValueError(
                    f"Provider '{provider_name}' requires environment variable "
                    f"{api_key_env}"
                )
            kwargs["api_key"] = api_key

        return kwargs
