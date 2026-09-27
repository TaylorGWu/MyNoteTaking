"""Prompt construction for structured note translation."""

import json


SUPPORTED_TARGET_LANGUAGES = (
    "Simplified Chinese",
    "Traditional Chinese",
    "Japanese",
)


def build_translation_messages(title: str, content: str, target_language: str) -> list[dict[str, str]]:
    """Build a provider-neutral request that requires a JSON object response."""

    note = json.dumps(
        {"title": title, "content": content, "target_language": target_language},
        ensure_ascii=False,
    )
    return [
        {
            "role": "system",
            "content": (
                "You are a precise note translator. Translate the title and content into "
                "the requested target language. Preserve Markdown, code blocks, URLs, "
                "identifiers, and paragraph structure. Return only a valid JSON object "
                "with exactly two string fields: title and content."
            ),
        },
        {
            "role": "user",
            "content": f"Translate this note. The requested input is JSON: {note}",
        },
    ]
