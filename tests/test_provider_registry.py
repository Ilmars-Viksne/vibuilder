import pytest

from providers.base import BaseProvider, ProviderRegistry


def test_provider_registration():
    @ProviderRegistry.register("test_provider")
    class TestProvider(BaseProvider):
        def chat(self, messages, temperature=0.2):
            return "test"

    provider = ProviderRegistry.create("test_provider", model="test-model")
    assert isinstance(provider, TestProvider)
    assert provider.chat([]) == "test"


def test_unknown_provider():
    with pytest.raises(ValueError):
        ProviderRegistry.create("unknown")


def test_googleai_provider_is_registered():
    import providers.googleai  # noqa: F401

    assert "googleai" in ProviderRegistry.available()


def test_googleai_provider_creation():
    from unittest.mock import patch
    import providers.googleai  # noqa: F401

    with patch("providers.googleai.genai.Client"):
        provider = ProviderRegistry.create(
            "googleai",
            model="gemma-4-31b-it",
            api_key="test-key",
        )

        assert provider.model == "gemma-4-31b-it"
