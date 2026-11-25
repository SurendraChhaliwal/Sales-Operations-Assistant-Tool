"""Product lookups."""

from src.data_loader import SalesData, records_from_frame


def get_product_details(data: SalesData, product_id: str) -> dict | list[dict]:
    matches = data.products[data.products["product_id"] == product_id]
    if matches.empty:
        return {"error": f"Product '{product_id}' was not found."}
    return records_from_frame(matches)
