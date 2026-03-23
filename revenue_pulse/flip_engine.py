"""
Flip ledger: buy + optional sold price; sourcing estimates via est_* columns;
variance when you later log actuals. Stdlib only.

  python3 -m revenue_pulse.flip_engine revenue_pulse/sample_flips.csv
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from revenue_pulse.revenue_engine import load_csv

DEFAULT_FEE_PERCENT = 15.0

BUY_ALIASES = frozenset(
    {"buy_cost", "buy_price", "cost", "purchase_price", "item_cost", "cogs"}
)
SALE_ALIASES = frozenset(
    {"sold_price", "sale_price", "sale_total", "amount", "gross_sale", "revenue"}
)
FEE_PCT_ALIASES = frozenset(
    {"fee_percent", "platform_fee_percent", "fvf_percent", "marketplace_fee_percent"}
)
FEE_AMT_ALIASES = frozenset({"fee_amount", "platform_fees", "total_fees", "fees"})
SHIP_ALIASES = frozenset(
    {"shipping_cost", "shipping_paid", "ship_cost", "shipping", "postage"}
)
DATE_ALIASES = frozenset(
    {"sale_date", "sold_date", "date", "order_date", "shipped_date"}
)
PURCHASE_DATE_ALIASES = frozenset(
    {"purchase_date", "buy_date", "sourced_date", "source_date"}
)
ITEM_ALIASES = frozenset({"item", "title", "product", "sku", "listing"})
TAX_ALIASES = frozenset(
    {"taxes", "sales_tax", "tax_paid", "tax_expense", "sales_taxes"}
)
PROMO_ALIASES = frozenset(
    {"promotion_fees", "promoted_listing", "ad_fees", "advertising", "ads"}
)
PACK_ALIASES = frozenset(
    {"packaging_cost", "shipping_materials", "materials", "supplies", "boxes_tape"}
)
MILEAGE_ALIASES = frozenset(
    {"mileage_cost", "mileage_dollars", "vehicle_mileage", "mileage_expense"}
)
# Sourcing-time estimates (before / without a completed sale)
EST_SALE_ALIASES = frozenset(
    {"est_sale_price", "estimated_sale", "target_sale", "expected_sale", "comp_price"}
)
EST_FEE_PCT_ALIASES = frozenset({"est_fee_percent", "estimated_fee_percent"})
EST_FEE_AMT_ALIASES = frozenset({"est_fee_amount", "estimated_fees"})
EST_SHIP_ALIASES = frozenset({"est_shipping", "estimated_shipping", "est_postage"})
EST_TAX_ALIASES = frozenset({"est_taxes", "estimated_taxes"})
EST_PROMO_ALIASES = frozenset({"est_promotion_fees", "est_ads", "estimated_promo"})
EST_PACK_ALIASES = frozenset({"est_packaging", "estimated_materials"})
EST_MILE_ALIASES = frozenset({"est_mileage_cost", "estimated_mileage"})


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def _parse_float(raw: str) -> float | None:
    s = str(raw).strip().replace(",", "")
    if not s:
        return None
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    s = re.sub(r"[^0-9.\-]", "", s)
    if s in {"", "-", "."}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date(raw: str) -> datetime | None:
    raw = str(raw).strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw[:19] if len(raw) > 19 else raw, fmt)
        except ValueError:
            continue
    return None


def detect_flip_columns(fieldnames: list[str]) -> dict[str, str | None]:
    norm_map = {_norm(f): f for f in fieldnames}
    out: dict[str, str | None] = {
        "buy": None,
        "sale": None,
        "fee_percent": None,
        "fee_amount": None,
        "shipping": None,
        "date": None,
        "purchase_date": None,
        "item": None,
        "taxes": None,
        "promotion_fees": None,
        "packaging": None,
        "mileage": None,
        "est_sale": None,
        "est_fee_percent": None,
        "est_fee_amount": None,
        "est_shipping": None,
        "est_taxes": None,
        "est_promotion_fees": None,
        "est_packaging": None,
        "est_mileage": None,
    }
    for n, original in norm_map.items():
        if out["buy"] is None and n in BUY_ALIASES:
            out["buy"] = original
        if out["sale"] is None and n in SALE_ALIASES:
            out["sale"] = original
        if out["fee_percent"] is None and n in FEE_PCT_ALIASES:
            out["fee_percent"] = original
        if out["fee_amount"] is None and n in FEE_AMT_ALIASES:
            out["fee_amount"] = original
        if out["shipping"] is None and n in SHIP_ALIASES:
            out["shipping"] = original
        if out["date"] is None and n in DATE_ALIASES:
            out["date"] = original
        if out["purchase_date"] is None and n in PURCHASE_DATE_ALIASES:
            out["purchase_date"] = original
        if out["item"] is None and n in ITEM_ALIASES:
            out["item"] = original
        if out["taxes"] is None and n in TAX_ALIASES:
            out["taxes"] = original
        if out["promotion_fees"] is None and n in PROMO_ALIASES:
            out["promotion_fees"] = original
        if out["packaging"] is None and n in PACK_ALIASES:
            out["packaging"] = original
        if out["mileage"] is None and n in MILEAGE_ALIASES:
            out["mileage"] = original
        if out["est_sale"] is None and n in EST_SALE_ALIASES:
            out["est_sale"] = original
        if out["est_fee_percent"] is None and n in EST_FEE_PCT_ALIASES:
            out["est_fee_percent"] = original
        if out["est_fee_amount"] is None and n in EST_FEE_AMT_ALIASES:
            out["est_fee_amount"] = original
        if out["est_shipping"] is None and n in EST_SHIP_ALIASES:
            out["est_shipping"] = original
        if out["est_taxes"] is None and n in EST_TAX_ALIASES:
            out["est_taxes"] = original
        if out["est_promotion_fees"] is None and n in EST_PROMO_ALIASES:
            out["est_promotion_fees"] = original
        if out["est_packaging"] is None and n in EST_PACK_ALIASES:
            out["est_packaging"] = original
        if out["est_mileage"] is None and n in EST_MILE_ALIASES:
            out["est_mileage"] = original
    if out["buy"] is None:
        for n, o in norm_map.items():
            if "buy" in n or (n.endswith("_cost") and "fee" not in n and not n.startswith("est")):
                out["buy"] = o
                break
    if out["sale"] is None:
        for n, o in norm_map.items():
            if any(x in n for x in ("sold", "sale", "gross")) and "fee" not in n and not n.startswith("est"):
                out["sale"] = o
                break
    return out


def _col_float(row: dict[str, str], col: str | None) -> float:
    if not col:
        return 0.0
    v = _parse_float(row.get(col, ""))
    return v if v is not None else 0.0


def _compute_actual_profit(
    row: dict[str, str],
    buy: float,
    sale: float,
    columns: dict[str, str | None],
    default_fee_percent: float,
) -> tuple[float, float, float, float, float, float, float, float, float, float]:
    """Returns fees, ship, taxes, promo, pack, mile, extra, net_proceeds, profit, roi."""
    fee_pct_col = columns.get("fee_percent")
    fee_amt_col = columns.get("fee_amount")
    ship_col = columns.get("shipping")
    tax_col = columns.get("taxes")
    promo_col = columns.get("promotion_fees")
    pack_col = columns.get("packaging")
    mile_col = columns.get("mileage")

    fee_pct = default_fee_percent
    if fee_pct_col and row.get(fee_pct_col, "").strip():
        v = _parse_float(row[fee_pct_col])
        if v is not None:
            fee_pct = v

    ship = 0.0
    if ship_col:
        v = _parse_float(row.get(ship_col, ""))
        if v is not None:
            ship = v

    if fee_amt_col and row.get(fee_amt_col, "").strip():
        v = _parse_float(row[fee_amt_col])
        fees = v if v is not None else sale * (fee_pct / 100.0)
    else:
        fees = sale * (fee_pct / 100.0)

    net_proceeds = sale - fees - ship
    taxes = _col_float(row, tax_col)
    promo = _col_float(row, promo_col)
    packaging = _col_float(row, pack_col)
    mileage = _col_float(row, mile_col)
    extra_costs = taxes + promo + packaging + mileage
    profit = net_proceeds - buy - extra_costs
    roi = (profit / buy * 100.0) if buy > 0 else 0.0
    return fees, ship, taxes, promo, packaging, mileage, extra_costs, net_proceeds, profit, roi


def _compute_estimate_profit(
    row: dict[str, str],
    buy: float,
    est_sale: float,
    columns: dict[str, str | None],
    default_fee_percent: float,
) -> tuple[float, float, float, float, float, float, float, float, float, float]:
    """Same shape as actual, using est_* columns and est_sale as gross."""
    fee_pct_col = columns.get("est_fee_percent")
    fee_amt_col = columns.get("est_fee_amount")
    ship_col = columns.get("est_shipping")
    tax_col = columns.get("est_taxes")
    promo_col = columns.get("est_promotion_fees")
    pack_col = columns.get("est_packaging")
    mile_col = columns.get("est_mileage")

    fee_pct = default_fee_percent
    if fee_pct_col and row.get(fee_pct_col, "").strip():
        v = _parse_float(row[fee_pct_col])
        if v is not None:
            fee_pct = v

    ship = 0.0
    if ship_col:
        v = _parse_float(row.get(ship_col, ""))
        if v is not None:
            ship = v

    if fee_amt_col and row.get(fee_amt_col, "").strip():
        v = _parse_float(row[fee_amt_col])
        fees = v if v is not None else est_sale * (fee_pct / 100.0)
    else:
        fees = est_sale * (fee_pct / 100.0)

    net_proceeds = est_sale - fees - ship
    taxes = _col_float(row, tax_col)
    promo = _col_float(row, promo_col)
    packaging = _col_float(row, pack_col)
    mileage = _col_float(row, mile_col)
    extra_costs = taxes + promo + packaging + mileage
    profit = net_proceeds - buy - extra_costs
    roi = (profit / buy * 100.0) if buy > 0 else 0.0
    return fees, ship, taxes, promo, packaging, mileage, extra_costs, net_proceeds, profit, roi


def analyze_flips(
    rows: list[dict[str, str]],
    columns: dict[str, str | None],
    default_fee_percent: float = DEFAULT_FEE_PERCENT,
) -> dict[str, Any]:
    buy_col = columns.get("buy")
    sale_col = columns.get("sale")
    date_col = columns.get("date")
    purchase_date_col = columns.get("purchase_date")
    item_col = columns.get("item")
    est_sale_col = columns.get("est_sale")

    if not buy_col:
        raise ValueError("Need a buy column (e.g. buy_cost, cost).")

    line_items: list[dict[str, Any]] = []
    total_actual_profit = 0.0
    total_estimated_profit_pending = 0.0
    total_buy_sold = 0.0
    total_buy_pending = 0.0
    total_sale_gross = 0.0
    sum_variance = 0.0
    variance_n = 0
    by_month: dict[str, dict[str, float]] = defaultdict(lambda: {"profit": 0.0, "count": 0})
    by_month_est: dict[str, dict[str, float]] = defaultdict(lambda: {"profit": 0.0, "count": 0})

    for i, row in enumerate(rows):
        buy = _parse_float(row.get(buy_col, ""))
        if buy is None:
            continue

        label = ""
        if item_col and row.get(item_col, "").strip():
            label = str(row[item_col]).strip()[:60]

        sale = _parse_float(row.get(sale_col, "")) if sale_col else None
        est_sale_val = _parse_float(row.get(est_sale_col, "")) if est_sale_col else None

        estimated_block: dict[str, Any] = {}
        if est_sale_val is not None:
            ef, es, etx, epr, epk, emi, eex, enp, eprofit, eroi = _compute_estimate_profit(
                row, buy, est_sale_val, columns, default_fee_percent
            )
            estimated_block = {
                "est_sale_price": round(est_sale_val, 2),
                "estimated_fees": round(ef, 2),
                "estimated_shipping": round(es, 2),
                "estimated_extras": round(eex, 2),
                "estimated_net_proceeds": round(enp, 2),
                "estimated_profit": round(eprofit, 2),
                "estimated_roi_percent": round(eroi, 1),
            }

        if sale is None:
            if est_sale_val is None:
                continue
            total_estimated_profit_pending += estimated_block["estimated_profit"]
            total_buy_pending += buy
            month_key = "unknown"
            if purchase_date_col:
                d = _parse_date(row.get(purchase_date_col, ""))
                if d:
                    month_key = d.strftime("%Y-%m")
            elif date_col:
                d = _parse_date(row.get(date_col, ""))
                if d:
                    month_key = d.strftime("%Y-%m")
            by_month_est[month_key]["profit"] += estimated_block["estimated_profit"]
            by_month_est[month_key]["count"] += 1

            line_items.append(
                {
                    "row": i + 2,
                    "status": "pending",
                    "item": label or f"row {i + 2}",
                    "buy_cost": round(buy, 2),
                    **estimated_block,
                    "actual_profit": None,
                    "variance_estimate_vs_actual": None,
                    "month": month_key,
                }
            )
            continue

        # Sold row
        af, ash, atx, apr, apk, ami, aex, anp, aprofit, aroi = _compute_actual_profit(
            row, buy, sale, columns, default_fee_percent
        )
        total_actual_profit += aprofit
        total_buy_sold += buy
        total_sale_gross += sale

        month_key = "unknown"
        if date_col:
            d = _parse_date(row.get(date_col, ""))
            if d:
                month_key = d.strftime("%Y-%m")
        by_month[month_key]["profit"] += aprofit
        by_month[month_key]["count"] += 1

        variance = None
        if est_sale_val is not None:
            variance = round(aprofit - estimated_block["estimated_profit"], 2)
            sum_variance += variance
            variance_n += 1

        line_items.append(
            {
                "row": i + 2,
                "status": "sold",
                "item": label or f"row {i + 2}",
                "buy_cost": round(buy, 2),
                "sale_price": round(sale, 2),
                "fees": round(af, 2),
                "shipping": round(ash, 2),
                "taxes": round(atx, 2),
                "promotion_fees": round(apr, 2),
                "packaging": round(apk, 2),
                "mileage": round(ami, 2),
                "extra_costs": round(aex, 2),
                "net_proceeds": round(anp, 2),
                "actual_profit": round(aprofit, 2),
                "actual_roi_percent": round(aroi, 1),
                **estimated_block,
                "variance_estimate_vs_actual": variance,
                "month": month_key,
            }
        )

    sold_rows = [x for x in line_items if x.get("status") == "sold"]
    pending_rows = [x for x in line_items if x.get("status") == "pending"]

    sorted_months = sorted(by_month.keys())
    sorted_months_est = sorted(by_month_est.keys())

    sum_taxes = sum(f.get("taxes", 0) or 0 for f in sold_rows)
    sum_promo = sum(f.get("promotion_fees", 0) or 0 for f in sold_rows)
    sum_pack = sum(f.get("packaging", 0) or 0 for f in sold_rows)
    sum_mile = sum(f.get("mileage", 0) or 0 for f in sold_rows)
    sum_extra = sum(f.get("extra_costs", 0) or 0 for f in sold_rows)

    return {
        "sold_count": len(sold_rows),
        "pending_count": len(pending_rows),
        "flip_count": len(line_items),
        "total_buy_sold": round(total_buy_sold, 2),
        "total_buy_pending_inventory": round(total_buy_pending, 2),
        "total_sale_gross": round(total_sale_gross, 2),
        "total_actual_profit": round(total_actual_profit, 2),
        "total_estimated_profit_pending": round(total_estimated_profit_pending, 2),
        "average_actual_profit_per_sold": round(
            total_actual_profit / len(sold_rows), 2
        )
        if sold_rows
        else 0.0,
        "portfolio_roi_sold_percent": round(
            (total_actual_profit / total_buy_sold * 100.0) if total_buy_sold > 0 else 0.0,
            1,
        ),
        "average_variance_estimate_vs_actual": round(sum_variance / variance_n, 2)
        if variance_n
        else None,
        "variance_rows_count": variance_n,
        "totals_taxes": round(sum_taxes, 2),
        "totals_promotion_fees": round(sum_promo, 2),
        "totals_packaging": round(sum_pack, 2),
        "totals_mileage": round(sum_mile, 2),
        "totals_extra_costs": round(sum_extra, 2),
        "profit_by_month": [
            {
                "period": m,
                "profit": round(by_month[m]["profit"], 2),
                "flips": int(by_month[m]["count"]),
            }
            for m in sorted_months
        ],
        "estimated_profit_by_month_pending": [
            {
                "period": m,
                "estimated_profit": round(by_month_est[m]["profit"], 2),
                "items": int(by_month_est[m]["count"]),
            }
            for m in sorted_months_est
        ],
        "flips": line_items,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 -m revenue_pulse.flip_engine <flips.csv>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    fieldnames, rows = load_csv(path)
    cols = detect_flip_columns(fieldnames)
    result = analyze_flips(rows, cols)
    result["_detected_columns"] = cols
    result["_default_fee_percent_if_no_column"] = DEFAULT_FEE_PERCENT
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
