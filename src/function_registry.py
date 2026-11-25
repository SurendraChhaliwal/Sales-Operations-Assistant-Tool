"""Map assistant tool names to business functions."""

from collections.abc import Callable
from typing import Any

from src.data_loader import SalesData
from src.tools.calculations import calculate_order_value
from src.tools.customers import get_customer_details
from src.tools.orders import get_customer_orders, get_order_details
from src.tools.payments import get_payment_status
from src.tools.products import get_product_details


ToolFunction = Callable[..., dict | list[dict]]


def build_function_registry(data: SalesData) -> dict[str, ToolFunction]:
    """Create the tool registry bound to the loaded sales data."""
    return {
        "get_customer_details": lambda **kwargs: get_customer_details(data, **kwargs),
        "get_customer_orders": lambda **kwargs: get_customer_orders(data, **kwargs),
        "get_order_details": lambda **kwargs: get_order_details(data, **kwargs),
        "get_product_details": lambda **kwargs: get_product_details(data, **kwargs),
        "get_payment_status": lambda **kwargs: get_payment_status(data, **kwargs),
        "calculate_order_value": calculate_order_value,
    }
