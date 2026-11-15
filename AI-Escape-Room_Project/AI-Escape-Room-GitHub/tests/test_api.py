from unittest.mock import Mock, patch
import pytest
import requests
from escape_room.llm import generate, LLMError


def test_no_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(LLMError, match="No API key"):
        generate("system", [{"role":"user", "content":"hello"}])


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500])
def test_http_errors_redact_provider_details(monkeypatch, status):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-token")
    with patch("escape_room.llm.requests.post", return_value=Mock(status_code=status)):
        with pytest.raises(LLMError) as error:
            generate("system", [{"role":"user", "content":"hi"}])
    assert "fake-test-token" not in str(error.value)


def test_rest_contract(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-token")
    response = Mock(status_code=200)
    response.json.return_value = {"candidates":[{"content":{"parts":[{"text":"Hi"}]}}]}
    with patch("escape_room.llm.requests.post", return_value=response) as post:
        assert generate("system", [{"role":"assistant", "content":"hello"}, {"role":"user", "content":"look"}]) == "Hi"
    args = post.call_args
    assert "fake-test-token" not in args.args[0]
    assert args.kwargs["headers"]["x-goog-api-key"] == "fake-test-token"
    assert args.kwargs["json"]["contents"][0]["role"] == "model"
    assert args.kwargs["timeout"] == (5, 25)


def test_network_timeout(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-token")
    with patch("escape_room.llm.requests.post", side_effect=requests.Timeout):
        with pytest.raises(LLMError, match="unavailable"):
            generate("system", [{"role":"user", "content":"hi"}])


@pytest.mark.parametrize("payload", [{}, {"candidates":[]}, {"candidates":[{"content":{"parts":[]}}]}])
def test_malformed_or_blocked_response(monkeypatch, payload):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-token")
    response = Mock(status_code=200)
    response.json.return_value = payload
    with patch("escape_room.llm.requests.post", return_value=response):
        with pytest.raises(LLMError):
            generate("system", [{"role":"user", "content":"hi"}])
