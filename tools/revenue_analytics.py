from __future__ import annotations

import json
from pathlib import Path

from crewai.tools import tool


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@tool("sales_csv_summary")
def sales_csv_summary(csv_path: str) -> str:
    """
    Summarize sales/revenue from a CSV export (columns like date, amount/revenue, optional product/customer).
    Pass a path relative to the project root (e.g. revenue_pulse/sample_sales.csv) or an absolute path.
    Returns JSON with totals, revenue by month, and top products/customers.
    """
    from revenue_pulse.revenue_engine import analyze_rows, detect_columns, load_csv

    root = _project_root()
    p = Path(csv_path).expanduser()
    if not p.is_absolute():
        p = (root / p).resolve()
    if not p.is_file():
        return f"File not found: {p}"
    try:
        fieldnames, rows = load_csv(p)
        cols = detect_columns(fieldnames)
        result = analyze_rows(rows, cols)
        result["_detected_columns"] = cols
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Analysis failed: {e}"
