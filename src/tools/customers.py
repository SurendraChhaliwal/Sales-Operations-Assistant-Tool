"""Customer lookups."""

from src.data_loader import SalesData, records_from_frame


def get_customer_details(data: SalesData, customer_id: str) -> dict | list[dict]:
    matches = data.customers[data.customers["customer_id"] == customer_id]
    if matches.empty:
        return {"error": f"Customer '{customer_id}' was not found."}
    return records_from_frame(matches)
