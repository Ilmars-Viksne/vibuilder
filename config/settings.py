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

    @property
    def active_provider(self):
        return self.config.get("provider", "ollama")

    def get_provider_config(self, provider_name):
        return self.config.get("providers", {}).get(provider_name, {})
