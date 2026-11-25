"""Load project settings and resolve project-relative paths."""

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load YAML settings and reject an empty or malformed configuration."""
    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ValueError(f"Configuration must be a YAML mapping: {config_path}")

    assistant = config.get("assistant")
    if not isinstance(assistant, dict):
        raise ValueError("Configuration must contain an 'assistant' mapping.")
    if not assistant.get("model"):
        raise ValueError("Configuration must define assistant.model.")
    if not isinstance(assistant.get("max_rounds"), int) or assistant["max_rounds"] < 1:
        raise ValueError("assistant.max_rounds must be a positive integer.")
    if not assistant.get("data_file"):
        raise ValueError("Configuration must define assistant.data_file.")
    if not config.get("output_dir"):
        raise ValueError("Configuration must define output_dir.")

    return config


def resolve_project_path(path_value: str) -> Path:
    """Resolve an absolute path as-is or a relative path from the project root."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
