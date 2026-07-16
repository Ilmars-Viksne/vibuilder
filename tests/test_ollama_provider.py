from unittest.mock import Mock, patch

import pytest
import requests

from providers.errors import ProviderUnavailableError
from providers.ollama import OllamaProvider


@patch("requests.post")
def test_ollama_translates_timeout(mock_post):
    provider = OllamaProvider(model="test-model")
    mock_post.side_effect = requests.Timeout("Timeout occurred")

    with pytest.raises(ProviderUnavailableError) as exc_info:
        provider.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.provider == "Ollama"
    assert "timed out" in exc_info.value.args[0]


@patch("requests.post")
def test_ollama_translates_connection_error(mock_post):
    provider = OllamaProvider(model="test-model")
    mock_post.side_effect = requests.ConnectionError("Connection refused")

    with pytest.raises(ProviderUnavailableError) as exc_info:
        provider.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.provider == "Ollama"
    assert "Could not connect to Ollama" in exc_info.value.args[0]


@patch("requests.post")
def test_ollama_translates_http_error(mock_post):
    provider = OllamaProvider(model="test-model")

    response = requests.Response()
    response.status_code = 500
    mock_post.side_effect = requests.HTTPError("Internal Server Error", response=response)

    with pytest.raises(ProviderUnavailableError) as exc_info:
        provider.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.provider == "Ollama"
    assert "HTTP error" in exc_info.value.args[0]


@patch("requests.post")
def test_ollama_translates_empty_response(mock_post):
    provider = OllamaProvider(model="test-model")

    response = Mock()
    response.json.return_value = {"message": {"content": ""}}
    mock_post.return_value = response

    with pytest.raises(ProviderUnavailableError) as exc_info:
        provider.chat([{"role": "user", "content": "Hello"}])

    assert exc_info.value.provider == "Ollama"
    assert "empty response" in exc_info.value.args[0]
