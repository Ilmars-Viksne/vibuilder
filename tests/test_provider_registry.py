import pytest
from providers.base import ProviderRegistry, BaseProvider

def test_provider_registration():
    @ProviderRegistry.register("test_provider")
    class TestProvider(BaseProvider):
        def chat(self, messages, temperature=0.2):
            return "test"

    assert "test_provider" in ProviderRegistry.available()
    provider = ProviderRegistry.create("test_provider", model="test-model")
    assert isinstance(provider, TestProvider)
    assert provider.model == "test-model"

def test_unknown_provider():
    with pytest.raises(ValueError) as excinfo:
        ProviderRegistry.create("unknown")
    assert "Provider 'unknown' not found" in str(excinfo.value)
