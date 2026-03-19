import csv
import os
from datetime import datetime
from pathlib import Path

from main import build_crew


def _safe(s: str) -> str:
  return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in s)[:80]


def main() -> None:
  base = Path(__file__).resolve().parent
  outputs_dir = base / "outputs"
  outputs_dir.mkdir(parents=True, exist_ok=True)

  manifest_path = Path(os.getenv("MANIFEST", str(base / "manifest.csv"))).expanduser()
  if not manifest_path.exists():
    raise SystemExit(f"Manifest not found: {manifest_path}")

  crew = build_crew()

  ts = datetime.now().strftime("%Y%m%d-%H%M%S")
  summary_path = outputs_dir / f"{ts}_manifest_summary.csv"

  with manifest_path.open(newline="", encoding="utf-8") as f_in, summary_path.open(
    "w", newline="", encoding="utf-8"
  ) as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(
      f_out,
      fieldnames=[
        "product",
        "target_price",
        "min_profit",
        "min_roi_percent",
        "result_file",
      ],
    )
    writer.writeheader()

    for row in reader:
      product = (row.get("product") or "").strip()
      if not product:
        continue

      target_price = (row.get("target_price") or "200").strip()
      min_profit = (row.get("min_profit") or os.getenv("MIN_PROFIT", "50")).strip()
      min_roi_percent = (row.get("min_roi_percent") or os.getenv("MIN_ROI_PERCENT", "30")).strip()

      result = crew.kickoff(
        inputs={
          "product": product,
          "target_price": target_price,
          "min_profit": min_profit,
          "min_roi_percent": min_roi_percent,
        }
      )

      out_path = outputs_dir / f"{ts}_{_safe(product)}_buy{_safe(target_price)}.txt"
      out_path.write_text(result.raw or "", encoding="utf-8")

      writer.writerow(
        {
          "product": product,
          "target_price": target_price,
          "min_profit": min_profit,
          "min_roi_percent": min_roi_percent,
          "result_file": str(out_path.relative_to(base)),
        }
      )

  print(f"Wrote summary: {summary_path}")


if __name__ == "__main__":
  main()

