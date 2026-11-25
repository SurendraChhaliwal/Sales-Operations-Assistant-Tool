"""Sales calculations."""

import math


def calculate_order_value(quantity: int | float, unit_price: int | float) -> dict[str, int | float]:
    """Calculate an extended order value from a quantity and unit price."""
    if isinstance(quantity, bool) or not isinstance(quantity, (int, float)):
        raise ValueError("quantity must be a number.")
    if isinstance(unit_price, bool) or not isinstance(unit_price, (int, float)):
        raise ValueError("unit_price must be a number.")
    if not math.isfinite(quantity) or not math.isfinite(unit_price):
        raise ValueError("quantity and unit_price must be finite numbers.")
    if quantity < 0 or unit_price < 0:
        raise ValueError("quantity and unit_price cannot be negative.")

    return {
        "quantity": quantity,
        "unit_price": unit_price,
        "total": round(quantity * unit_price, 2)
    }
