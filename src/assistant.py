"""OpenAI assistant/tool interaction loop."""

from typing import Any

from openai import OpenAI

from src.function_registry import ToolFunction
from src.tool_executor import execute_tool


SYSTEM_PROMPT = """You are a Sales Operations Assistant.
Use the available tools as the source of truth for questions about customers, orders,
products, order values, and payment status. Do not invent business data. If a record
is missing, clearly say that it was not found. Present related order information in
a clear, readable format."""


def run_sales_assistant(
    query: str,
    client: OpenAI,
    tools: list[dict[str, Any]],
    registry: dict[str, ToolFunction],
    model: str,
    max_rounds: int = 8,
) -> str:
    """Run the bounded assistant/tool loop and return the final answer."""
    if not query.strip():
        raise ValueError("The user query cannot be empty.")
    if max_rounds < 1:
        raise ValueError("max_rounds must be a positive integer.")

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        if not response.choices:
            raise RuntimeError("The assistant returned no response choices.")

        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump(exclude_none=True))

        if not assistant_message.tool_calls:
            if assistant_message.content is None:
                raise RuntimeError("The assistant returned an empty final response.")
            return assistant_message.content

        for tool_call in assistant_message.tool_calls:
            messages.append(execute_tool(tool_call, registry))

    raise RuntimeError(
        f"The assistant did not finish within the configured {max_rounds} rounds."
    )
