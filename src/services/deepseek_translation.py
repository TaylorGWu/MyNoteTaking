"""Server-side integration with the official DeepSeek Chat Completions API."""

import json
from typing import Any

from openai import OpenAI

from src.config import ConfigurationError, get_required_setting
from src.prompts.translation import build_translation_messages


class TranslationError(RuntimeError):
    """A safe error that can be presented to an API caller."""


class DeepSeekTranslator:
    """Translate note fields without exposing the provider credential to clients."""

    def __init__(self, client: Any | None = None, timeout_seconds: float = 30.0):
        self._client = client
        self._timeout_seconds = timeout_seconds

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = OpenAI(
                api_key=get_required_setting("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com",
                timeout=self._timeout_seconds,
            )
        return self._client

    def translate(self, title: str, content: str, target_language: str) -> dict[str, str]:
        """Return provider output only after strict JSON shape validation."""

        try:
            response = self._get_client().chat.completions.create(
                model="deepseek-flash",
                messages=build_translation_messages(title, content, target_language),
                response_format={"type": "json_object"},
                max_tokens=4096,
                extra_body={"thinking": {"type": "disabled"}},
            )
            raw_content = response.choices[0].message.content
            translated_note = json.loads(raw_content or "")
        except ConfigurationError:
            raise
        except (json.JSONDecodeError, IndexError, KeyError, TypeError) as error:
            raise TranslationError("DeepSeek did not return a valid translation. Please try again.") from error
        except Exception as error:
            raise TranslationError("Translation is temporarily unavailable. Please try again.") from error

        if not isinstance(translated_note, dict):
            raise TranslationError("DeepSeek did not return a valid translation. Please try again.")

        translated_title = translated_note.get("title")
        translated_content = translated_note.get("content")
        if not isinstance(translated_title, str) or not isinstance(translated_content, str):
            raise TranslationError("DeepSeek did not return a valid translation. Please try again.")

        return {"title": translated_title, "content": translated_content}
