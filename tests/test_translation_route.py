import pytest
from flask import Flask

from src.config import ConfigurationError
from src.routes.translation import translation_bp
from src.services.deepseek_translation import TranslationError


class SuccessfulTranslator:
    def translate(self, title, content, target_language):
        return {"title": f"translated {title}", "content": f"translated {content}"}


class FailingTranslator:
    def translate(self, title, content, target_language):
        raise TranslationError("Translation is temporarily unavailable. Please try again.")


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(translation_bp, url_prefix="/api")
    return app


def test_translate_rejects_an_empty_note(app):
    client = app.test_client()

    response = client.post(
        "/api/translate",
        json={"title": "   ", "content": "", "target_language": "Japanese"},
    )

    assert response.status_code == 400
    assert "title or content" in response.get_json()["error"]


def test_translate_rejects_an_unsupported_target_language(app):
    client = app.test_client()

    response = client.post(
        "/api/translate",
        json={"title": "Hello", "content": "World", "target_language": "Klingon"},
    )

    assert response.status_code == 400
    assert "target language" in response.get_json()["error"]


def test_translate_returns_title_and_content_from_the_service(app):
    app.config["TRANSLATOR"] = SuccessfulTranslator()
    client = app.test_client()

    response = client.post(
        "/api/translate",
        json={"title": "Hello", "content": "World", "target_language": "Japanese"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"title": "translated Hello", "content": "translated World"}


def test_translate_returns_safe_error_when_service_fails(app):
    app.config["TRANSLATOR"] = FailingTranslator()
    client = app.test_client()

    response = client.post(
        "/api/translate",
        json={"title": "Hello", "content": "World", "target_language": "Japanese"},
    )

    assert response.status_code == 502
    assert response.get_json() == {"error": "Translation is temporarily unavailable. Please try again."}


def test_translate_reports_missing_server_configuration(app, monkeypatch):
    def missing_setting(_name):
        raise ConfigurationError("DEEPSEEK_API_KEY is missing")

    monkeypatch.setattr(
        "src.services.deepseek_translation.get_required_setting",
        missing_setting,
    )
    client = app.test_client()

    response = client.post(
        "/api/translate",
        json={"title": "Hello", "content": "World", "target_language": "Japanese"},
    )

    assert response.status_code == 503
    assert response.get_json() == {"error": "Translation is not configured on this server."}
