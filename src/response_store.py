"""Persist assistant responses as JSON files."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def save_response(response: dict[str, Any], output_dir: Path) -> Path:
    """Write a timestamped response and atomically update the latest-response file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_response = {
        **response,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    serialized = json.dumps(saved_response, ensure_ascii=False, indent=2, allow_nan=False)

    unique_name = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + f"_{uuid4().hex[:8]}.json"
    )
    saved_path = output_dir / unique_name
    saved_path.write_text(serialized + "\n", encoding="utf-8")

    temporary_path = output_dir / f".latest_{uuid4().hex}.tmp"
    try:
        temporary_path.write_text(serialized + "\n", encoding="utf-8")
        temporary_path.replace(output_dir / "latest_response.json")
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return saved_path
