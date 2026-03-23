"""
Sales / revenue analytics using only the Python standard library.
Usage: python3 -m revenue_pulse.revenue_engine path/to/sales.csv
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

AMOUNT_ALIASES = frozenset(
    {
        "amount",
        "revenue",
        "total",
        "sale",
        "sales",
        "price",
        "subtotal",
        "value",
        "payment",
        "gross_sales",
        "net_sales",
        "gross_amount",
        "net_amount",
        "extended_price",
        "line_total",
        "item_total",
        "charged_amount",
        "payout",
        "net_paid",
        "net_payment",
        "settlement",
        "transfer_amount",
    }
)
DATE_ALIASES = frozenset(
    {"date", "order_date", "purchased_at", "created_at", "invoice_date", "day"}
)
PRODUCT_ALIASES = frozenset({"product", "sku", "item", "line_item"})
CUSTOMER_ALIASES = frozenset({"customer", "client", "account", "email"})


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def _parse_date(raw: str) -> datetime | None:
    raw = raw.strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw[:19] if len(raw) > 19 else raw, fmt)
        except ValueError:
            continue
    return None


def _parse_amount(raw: str) -> float | None:
    s = raw.strip().replace(",", "")
    if not s:
        return None
    if s[0] == "(" and s[-1] == ")":
        s = "-" + s[1:-1]
    cleaned = re.sub(r"[^0-9.\-]", "", s)
    if cleaned in {"", "-", "."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def detect_columns(fieldnames: list[str]) -> dict[str, str | None]:
    norm_map = {_norm(f): f for f in fieldnames}
    out: dict[str, str | None] = {
        "date": None,
        "amount": None,
        "product": None,
        "customer": None,
    }
    for n, original in norm_map.items():
        if out["amount"] is None and (n in AMOUNT_ALIASES or n.endswith("_amount")):
            out["amount"] = original
        if out["date"] is None and (n in DATE_ALIASES or n.endswith("_date")):
            out["date"] = original
        if out["product"] is None and n in PRODUCT_ALIASES:
            out["product"] = original
        if out["customer"] is None and n in CUSTOMER_ALIASES:
            out["customer"] = original
    if out["amount"] is None:
        for n, original in norm_map.items():
            if "total" in n or "revenue" in n or "amount" in n:
                out["amount"] = original
                break
    return out


def analyze_rows(
    rows: list[dict[str, str]], columns: dict[str, str | None]
) -> dict[str, Any]:
    date_col = columns.get("date")
    amount_col = columns.get("amount")
    product_col = columns.get("product")
    customer_col = columns.get("customer")

    if not amount_col:
        raise ValueError("Could not find an amount column (e.g. amount, revenue, total).")

    total = 0.0
    count = 0
    by_month: dict[str, float] = defaultdict(float)
    by_product: dict[str, float] = defaultdict(float)
    by_customer: dict[str, float] = defaultdict(float)

    for row in rows:
        raw_amt = row.get(amount_col, "")
        amt = _parse_amount(raw_amt)
        if amt is None:
            continue
        total += amt
        count += 1

        d = None
        if date_col:
            d = _parse_date(row.get(date_col, ""))
        month_key = d.strftime("%Y-%m") if d else "unknown"
        by_month[month_key] += amt

        if product_col and row.get(product_col, "").strip():
            by_product[row[product_col].strip()[:80]] += amt
        if customer_col and row.get(customer_col, "").strip():
            by_customer[row[customer_col].strip()[:80]] += amt

    sorted_months = sorted(by_month.keys())
    avg = total / count if count else 0.0

    def top_n(d: dict[str, float], n: int = 10) -> list[dict[str, Any]]:
        items = sorted(d.items(), key=lambda x: -x[1])[:n]
        return [{"name": k, "revenue": round(v, 2)} for k, v in items]

    return {
        "total_revenue": round(total, 2),
        "transaction_count": count,
        "average_order_value": round(avg, 2),
        "revenue_by_month": [
            {"period": m, "revenue": round(by_month[m], 2)} for m in sorted_months
        ],
        "top_products": top_n(by_product) if product_col else [],
        "top_customers": top_n(by_customer) if customer_col else [],
    }


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    fieldnames = reader.fieldnames or []
    rows = [dict(r) for r in reader if any(v.strip() for v in r.values())]
    return list(fieldnames), rows


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 -m revenue_pulse.revenue_engine <sales.csv>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    fieldnames, rows = load_csv(path)
    cols = detect_columns(fieldnames)
    result = analyze_rows(rows, cols)
    result["_detected_columns"] = cols
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
