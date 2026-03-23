from __future__ import annotations

import json
from pathlib import Path

from crewai.tools import tool


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@tool("flip_csv_summary")
def flip_csv_summary(csv_path: str) -> str:
    """
    Analyze a flip ledger CSV: columns for buy cost and sold/sale price; optional fee_percent,
    fee_amount, shipping_cost, sale_date, item. Returns JSON with per-flip profit, ROI, and monthly totals.
    Path relative to project root or absolute (e.g. revenue_pulse/sample_flips.csv).
    """
    from revenue_pulse.flip_engine import analyze_flips, detect_flip_columns
    from revenue_pulse.revenue_engine import load_csv

    root = _project_root()
    p = Path(csv_path).expanduser()
    if not p.is_absolute():
        p = (root / p).resolve()
    if not p.is_file():
        return f"File not found: {p}"
    try:
        fieldnames, rows = load_csv(p)
        cols = detect_flip_columns(fieldnames)
        result = analyze_flips(rows, cols)
        result["_detected_columns"] = cols
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Flip analysis failed: {e}"
