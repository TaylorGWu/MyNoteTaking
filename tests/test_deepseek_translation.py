from types import SimpleNamespace

import pytest

from src.services.deepseek_translation import DeepSeekTranslator, TranslationError


def _client_returning(content):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    completions = SimpleNamespace(create=lambda **_kwargs: response)
    return SimpleNamespace(chat=SimpleNamespace(completions=completions))


def test_translate_returns_validated_title_and_content():
    client = _client_returning('{"title": "こんにちは", "content": "世界"}')
    translator = DeepSeekTranslator(client=client)

    result = translator.translate("Hello", "World", "Japanese")

    assert result == {"title": "こんにちは", "content": "世界"}


def test_translate_rejects_malformed_model_json():
    translator = DeepSeekTranslator(client=_client_returning("not json"))

    with pytest.raises(TranslationError, match="valid translation"):
        translator.translate("Hello", "World", "Japanese")


def test_translate_turns_provider_failures_into_safe_error():
    def raise_provider_error(**_kwargs):
        raise RuntimeError("provider error contains implementation details")

    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=raise_provider_error))
    )
    translator = DeepSeekTranslator(client=client)

    with pytest.raises(TranslationError, match="temporarily unavailable"):
        translator.translate("Hello", "World", "Japanese")
