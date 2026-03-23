from __future__ import annotations

from pathlib import Path

from revenue_pulse.revenue_engine import analyze_rows, detect_columns, load_csv


def test_detect_columns_payment_alias() -> None:
    cols = detect_columns(["date", "payment", "sku"])
    assert cols.get("amount") == "payment"


def test_detect_columns_gross_sales_alias() -> None:
    cols = detect_columns(["order_date", "gross_sales", "item"])
    assert cols.get("amount") == "gross_sales"


def test_sample_sales_csv(project_root: Path) -> None:
    path = project_root / "revenue_pulse" / "sample_sales.csv"
    fieldnames, rows = load_csv(path)
    cols = detect_columns(fieldnames)
    result = analyze_rows(rows, cols)

    assert result["total_revenue"] == 3630.99
    assert result["transaction_count"] == 8
    assert result["average_order_value"] == 453.87
    assert cols.get("amount") == "amount"
    assert cols.get("date") == "date"
