import os
import pytest
from config.settings import Settings

def test_settings_default_provider(monkeypatch):
    monkeypatch.delenv("DEFAULT_PROVIDER", raising=False)
    settings = Settings()
    # Assuming config.yaml has 'nim' as default from my previous read
    assert settings.resolve_provider() in ["nim", "ollama"]

def test_settings_cli_override():
    settings = Settings()
    assert settings.resolve_provider(cli_provider="mock") == "mock"

def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")
    settings = Settings()
    assert settings.resolve_provider() == "openrouter"

def test_get_provider_kwargs(monkeypatch):
    monkeypatch.setenv("MOCK_API_KEY", "test-key")
    settings = Settings()
    kwargs = settings.get_provider_kwargs("mock")
    assert kwargs["model"] == "mock-model"
    assert kwargs["api_key"] == "test-key"
