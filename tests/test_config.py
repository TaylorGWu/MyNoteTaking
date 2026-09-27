import os

import pytest

from src.config import ConfigurationError, get_required_setting


def test_environment_variable_takes_precedence_over_yaml(monkeypatch, tmp_path):
    config_file = tmp_path / "env.yaml"
    config_file.write_text("DEEPSEEK_API_KEY: yaml-value\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "environment-value")

    assert get_required_setting("DEEPSEEK_API_KEY", config_file) == "environment-value"


def test_yaml_is_used_when_environment_variable_is_missing(monkeypatch, tmp_path):
    config_file = tmp_path / "env.yaml"
    config_file.write_text("DEEPSEEK_API_KEY: yaml-value\n", encoding="utf-8")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    assert get_required_setting("DEEPSEEK_API_KEY", config_file) == "yaml-value"


def test_missing_setting_names_the_missing_variable(monkeypatch, tmp_path):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="DEEPSEEK_API_KEY"):
        get_required_setting("DEEPSEEK_API_KEY", tmp_path / "env.yaml")
