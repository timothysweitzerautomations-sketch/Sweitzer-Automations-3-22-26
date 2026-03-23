from __future__ import annotations

from pathlib import Path

from revenue_pulse.flip_engine import analyze_flips, detect_flip_columns, load_csv


def test_sample_flips_csv(project_root: Path) -> None:
    path = project_root / "revenue_pulse" / "sample_flips.csv"
    fieldnames, rows = load_csv(path)
    cols = detect_flip_columns(fieldnames)
    result = analyze_flips(rows, cols)

    assert result["sold_count"] == 6
    assert result["pending_count"] == 2
    assert result["flip_count"] == 8
    assert result["total_buy_sold"] == 209.0
    assert result["total_buy_pending_inventory"] == 23.0
    assert result["total_sale_gross"] == 585.0
    assert result["total_actual_profit"] == 189.91
    assert result["total_estimated_profit_pending"] == 31.0
    assert result["variance_rows_count"] == 6
    assert result["average_variance_estimate_vs_actual"] == -8.66
    assert cols.get("est_sale") == "est_sale_price"
    assert cols.get("purchase_date") == "purchase_date"
