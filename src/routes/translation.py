"""HTTP API for note translation."""

from flask import Blueprint, current_app, jsonify, request

from src.config import ConfigurationError
from src.prompts.translation import SUPPORTED_TARGET_LANGUAGES
from src.services.deepseek_translation import DeepSeekTranslator, TranslationError


translation_bp = Blueprint("translation", __name__)


def _get_translator():
    return current_app.config.get("TRANSLATOR") or DeepSeekTranslator()


@translation_bp.route("/translate", methods=["POST"])
def translate_note():
    """Translate one in-memory note without saving it."""

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON translation request is required."}), 400

    title = data.get("title", "")
    content = data.get("content", "")
    target_language = data.get("target_language", "")

    if not isinstance(title, str) or not isinstance(content, str):
        return jsonify({"error": "Title and content must be text."}), 400
    if not title.strip() and not content.strip():
        return jsonify({"error": "Provide a note title or content to translate."}), 400
    if target_language not in SUPPORTED_TARGET_LANGUAGES:
        return jsonify({"error": "Choose a supported target language."}), 400

    try:
        translated_note = _get_translator().translate(title, content, target_language)
    except ConfigurationError:
        return jsonify({"error": "Translation is not configured on this server."}), 503
    except TranslationError as error:
        return jsonify({"error": str(error)}), 502

    return jsonify(translated_note)
