"""Helpers for building OpenAI function-tool schemas."""

from typing import Any


def create_tool(
    name: str,
    description: str,
    properties: dict[str, dict[str, Any]],
    required: list[str],
) -> dict[str, Any]:
    """Build a function tool schema with an explicit, closed argument object."""
    if set(required) - set(properties):
        raise ValueError("Every required argument must be defined in properties.")

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }
