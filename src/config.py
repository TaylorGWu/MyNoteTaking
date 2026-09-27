"""Local and deployment configuration helpers."""

import os
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigurationError(RuntimeError):
    """Raised when a required application setting is unavailable."""


def _load_yaml_settings(yaml_path: Path) -> dict[str, Any]:
    if not yaml_path.is_file():
        return {}

    try:
        with yaml_path.open("r", encoding="utf-8") as config_file:
            settings = yaml.safe_load(config_file) or {}
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Could not parse local configuration file: {yaml_path}") from error

    if not isinstance(settings, dict):
        raise ConfigurationError(f"Local configuration file must contain key-value settings: {yaml_path}")

    return settings


def get_required_setting(name: str, yaml_path: Path | None = None) -> str:
    """Return a required setting from the environment or local YAML file.

    Deployment variables always win over local-only configuration. The YAML
    fallback exists for local development and must not be committed.
    """

    environment_value = os.environ.get(name, "").strip()
    if environment_value:
        return environment_value

    settings_path = yaml_path or PROJECT_ROOT / "env.yaml"
    yaml_value = _load_yaml_settings(settings_path).get(name, "")
    if isinstance(yaml_value, str) and yaml_value.strip():
        return yaml_value.strip()

    raise ConfigurationError(
        f"Missing required configuration setting: {name}. "
        "Set it as an environment variable or add it to local env.yaml."
    )
