"""Order lookups."""

from src.data_loader import SalesData, records_from_frame


def get_order_details(data: SalesData, order_id: str) -> dict | list[dict]:
    matches = data.orders[data.orders["order_id"] == order_id]
    if matches.empty:
        return {"error": f"Order '{order_id}' was not found."}
    return records_from_frame(matches)


def get_customer_orders(data: SalesData, customer_id: str) -> dict | list[dict]:
    customer_exists = (data.customers["customer_id"] == customer_id).any()
    if not customer_exists:
        return {"error": f"Customer '{customer_id}' was not found."}

    matches = data.orders[data.orders["customer_id"] == customer_id]
    return records_from_frame(matches)
