"""Validate and execute assistant-requested tools."""

import json
from typing import Any

from src.function_registry import ToolFunction


def execute_tool(tool_call: Any, registry: dict[str, ToolFunction]) -> dict[str, str]:
    """Run one tool call and return a Chat Completions tool message."""
    name = tool_call.function.name
    call_id = tool_call.id
    function = registry.get(name)
    if function is None:
        result: Any = {"error": f"Unknown tool '{name}'."}
        return _tool_message(call_id, result)

    try:
        arguments = json.loads(tool_call.function.arguments)
    except (json.JSONDecodeError, TypeError) as error:
        return _tool_message(call_id, {"error": f"Invalid tool arguments: {error}"})

    if not isinstance(arguments, dict):
        return _tool_message(call_id, {"error": "Tool arguments must be a JSON object."})

    try:
        result = function(**arguments)
    except (TypeError, ValueError) as error:
        result = {"error": f"Tool '{name}' could not be executed: {error}"}

    return _tool_message(call_id, result)


def _tool_message(call_id: str, result: Any) -> dict[str, str]:
    return {
        "role": "tool",
        "tool_call_id": call_id,
        "content": json.dumps(result, default=str, allow_nan=False),
    }
