"""Import and validate the sales workbook."""

from dataclasses import dataclass
from datetime import date, datetime
import math
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "Orders": {"order_id", "customer_id", "product_id", "quantity", "order_date", "status"},
    "Customers": {"customer_id", "customer_name", "city", "segment"},
    "Products": {"product_id", "product_name", "unit_price"},
    "Payments": {"payment_id", "order_id", "amount_paid", "due_date", "payment_status"},
}


@dataclass(frozen=True)
class SalesData:
    orders: pd.DataFrame
    customers: pd.DataFrame
    products: pd.DataFrame
    payments: pd.DataFrame


def load_sales_data(workbook_path: Path) -> SalesData:
    """Read the required worksheets and fail clearly if the workbook is incomplete."""
    if not workbook_path.is_file():
        raise FileNotFoundError(f"Sales workbook was not found: {workbook_path}")

    with pd.ExcelFile(workbook_path) as workbook:
        missing_sheets = set(REQUIRED_COLUMNS) - set(workbook.sheet_names)
        if missing_sheets:
            raise ValueError(
                "Sales workbook is missing required sheets: "
                + ", ".join(sorted(missing_sheets))
            )

        tables = {
            sheet_name: pd.read_excel(workbook, sheet_name=sheet_name)
            for sheet_name in REQUIRED_COLUMNS
        }

    for sheet_name, required_columns in REQUIRED_COLUMNS.items():
        missing_columns = required_columns - set(tables[sheet_name].columns)
        if missing_columns:
            raise ValueError(
                f"Sheet '{sheet_name}' is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

    return SalesData(
        orders=tables["Orders"],
        customers=tables["Customers"],
        products=tables["Products"],
        payments=tables["Payments"],
    )


def records_from_frame(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert dataframe rows into values that can be serialized as strict JSON."""
    return [
        {key: _json_safe(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _json_safe(value: Any) -> Any:
    if value is None or value is pd.NaT:
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
