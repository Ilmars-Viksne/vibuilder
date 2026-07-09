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

        with self.config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

        if "providers" not in data:
            raise ValueError("Config must contain a 'providers' section")

        return data

    def get_provider_name(self, override: str | None = None) -> str:
        if override:
            return override

        env_provider = os.getenv("DEFAULT_PROVIDER")
        if env_provider:
            return env_provider

        provider = self.config.get("provider")
        if not provider:
            raise ValueError("No default provider configured")

        return provider

    def get_provider_kwargs(self, provider_name: str) -> dict[str, Any]:
        providers = self.config.get("providers", {})
        if provider_name not in providers:
            available = ", ".join(sorted(providers))
            raise ValueError(
                f"Provider '{provider_name}' not found in config. "
                f"Available providers: {available}"
            )

        provider_config = dict(providers[provider_name])

        api_key_env = provider_config.pop("api_key_env", None)
        if api_key_env:
            api_key = os.getenv(api_key_env)
            if not api_key:
                raise ValueError(
                    f"Provider '{provider_name}' requires environment variable "
                    f"'{api_key_env}'"
                )
            provider_config["api_key"] = api_key

        return provider_config
