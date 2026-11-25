"""Payment lookups."""

from src.data_loader import SalesData, records_from_frame


def get_payment_status(data: SalesData, order_id: str) -> dict | list[dict]:
    matches = data.payments[data.payments["order_id"] == order_id]
    if matches.empty:
        return {"error": f"No payment record was found for order '{order_id}'."}
    return records_from_frame(matches)
