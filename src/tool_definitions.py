"""Definitions of the tools available to the assistant."""

from typing import Any

from src.tool_schema import create_tool


def build_tools() -> list[dict[str, Any]]:
    """Return tool schemas for supported sales operations."""
    return [
        create_tool(
            name="get_customer_details",
            description="Get customer details using a customer ID.",
            properties={"customer_id": {"type": "string"}},
            required=["customer_id"],
        ),
        create_tool(
            name="get_customer_orders",
            description="Get all orders for a customer ID.",
            properties={"customer_id": {"type": "string"}},
            required=["customer_id"],
        ),
        create_tool(
            name="get_order_details",
            description="Get order information, including quantity and status, using an order ID.",
            properties={"order_id": {"type": "string"}},
            required=["order_id"],
        ),
        create_tool(
            name="get_product_details",
            description="Get product information and unit price using a product ID.",
            properties={"product_id": {"type": "string"}},
            required=["product_id"],
        ),
        create_tool(
            name="get_payment_status",
            description="Get payment information and status using an order ID.",
            properties={"order_id": {"type": "string"}},
            required=["order_id"],
        ),
        create_tool(
            name="calculate_order_value",
            description="Calculate an order value using its quantity and unit price.",
            properties={
                "quantity": {"type": "number"},
                "unit_price": {"type": "number"},
            },
            required=["quantity", "unit_price"],
        ),
    ]
