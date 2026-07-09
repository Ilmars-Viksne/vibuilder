import os
import yaml
from pathlib import Path

class Settings:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            return {"provider": "ollama", "providers": {}}
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def resolve_provider(self, cli_provider=None):
        """
        Resolves provider using precedence:
        1. CLI --provider
        2. .env DEFAULT_PROVIDER
        3. config.yaml provider
        """
        if cli_provider:
            return cli_provider

        env_provider = os.getenv("DEFAULT_PROVIDER")
        if env_provider:
            return env_provider

        return self.config.get("provider", "ollama")

    def get_provider_config(self, provider_name):
        return self.config.get("providers", {}).get(provider_name, {})

    def get_provider_kwargs(self, provider_name):
        config = self.get_provider_config(provider_name)

        # Get API key from environment variable
        api_key_var = f"{provider_name.upper()}_API_KEY"
        api_key = os.getenv(api_key_var, "")

        kwargs = {
            "model": config.get("model", "default-model"),
            "api_key": api_key
        }

        # Merge any other provider-specific config
        for key, value in config.items():
            if key != "model":
                kwargs[key] = value

        return kwargs
