import pytest

from config.settings import Settings


CONFIG = """
provider: nim

providers:
  nim:
    model: meta/llama-3.3-70b-instruct
    api_key_env: NIM_API_KEY

  openrouter:
    model: anthropic/claude-3.5-sonnet
    api_key_env: OPENROUTER_API_KEY

  mock:
    model: mock-model
"""


def write_config(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(CONFIG, encoding="utf-8")
    return path


def test_settings_default_provider(tmp_path, monkeypatch):
    monkeypatch.delenv("DEFAULT_PROVIDER", raising=False)
    monkeypatch.setenv("NIM_API_KEY", "nim-key")

    settings = Settings(write_config(tmp_path))

    assert settings.get_provider_name() == "nim"
    assert settings.get_provider_kwargs("nim") == {
        "model": "meta/llama-3.3-70b-instruct",
        "api_key": "nim-key",
    }


def test_settings_cli_override(tmp_path):
    settings = Settings(write_config(tmp_path))

    assert settings.get_provider_name("mock") == "mock"


def test_settings_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")

    settings = Settings(write_config(tmp_path))

    assert settings.get_provider_name() == "openrouter"


def test_get_provider_kwargs_mock(tmp_path):
    settings = Settings(write_config(tmp_path))

    assert settings.get_provider_kwargs("mock") == {
        "model": "mock-model",
    }


def test_get_provider_kwargs_requires_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("NIM_API_KEY", raising=False)
    settings = Settings(write_config(tmp_path))

    with pytest.raises(ValueError):
        settings.get_provider_kwargs("nim")
