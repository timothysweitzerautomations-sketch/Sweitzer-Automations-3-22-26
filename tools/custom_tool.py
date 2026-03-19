from __future__ import annotations

from dataclasses import dataclass

from crewai.tools import tool


@dataclass(frozen=True)
class CustomToolResult:
  ok: bool
  value: str


def quick_math(expression: str) -> CustomToolResult:
  """
  Tiny example "tool" you can wire into CrewAI later.
  Keeps it intentionally minimal/safe (no eval).
  """
  allowed = set("0123456789+-*/(). ")
  if any(ch not in allowed for ch in expression):
    return CustomToolResult(ok=False, value="Unsupported characters in expression.")
  return CustomToolResult(ok=True, value=f"Received: {expression}")


@tool("ddg_search")
def ddg_search(query: str, max_results: int = 5) -> str:
  """DuckDuckGo search (no API key). Returns a compact text list of results."""
  try:
    from ddgs import DDGS
  except Exception as e:  # pragma: no cover
    return f"ddgs is not installed or failed to import: {e}"

  results: list[str] = []
  with DDGS() as ddgs:
    for r in ddgs.text(query, max_results=max_results):
      title = (r.get("title") or "").strip()
      href = (r.get("href") or r.get("url") or "").strip()
      body = (r.get("body") or "").strip()
      line = f"- {title} ({href})"
      if body:
        line += f"\n  {body}"
      results.append(line)

  return "\n".join(results) if results else "No results."


@tool("scrape_website")
def scrape_website(url: str, max_chars: int = 8000) -> str:
  """Fetch a URL and return readable text (best-effort)."""
  try:
    import requests
    from bs4 import BeautifulSoup
  except Exception as e:  # pragma: no cover
    return f"Missing dependencies for scraping: {e}"

  try:
    resp = requests.get(
      url,
      headers={"User-Agent": "Mozilla/5.0"},
      timeout=20,
    )
    resp.raise_for_status()
  except Exception as e:
    return f"Failed to fetch {url}: {e}"

  soup = BeautifulSoup(resp.text, "html.parser")
  for tag in soup(["script", "style", "noscript"]):
    tag.decompose()

  text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
  if len(text) > max_chars:
    text = text[:max_chars] + "\n...[truncated]"
  return text


@tool("fee_calculator")
def fee_calculator(
  *,
  expected_sale_price: float,
  buy_price: float,
  fee_percent: float = 15.0,
  shipping_cost: float = 10.0,
) -> str:
  """
  Calculate net proceeds, profit, ROI%, and breakeven sale price.
  """
  fee_rate = max(fee_percent, 0.0) / 100.0
  fees = expected_sale_price * fee_rate
  net = expected_sale_price - fees - shipping_cost
  profit = net - buy_price
  roi = (profit / buy_price * 100.0) if buy_price else 0.0
  breakeven_sale = (buy_price + shipping_cost) / (1.0 - fee_rate) if fee_rate < 1.0 else float("inf")
  return (
    f"expected_sale_price=${expected_sale_price:.2f}\n"
    f"buy_price=${buy_price:.2f}\n"
    f"fee_percent={fee_percent:.2f}% (fees=${fees:.2f})\n"
    f"shipping_cost=${shipping_cost:.2f}\n"
    f"net_proceeds=${net:.2f}\n"
    f"net_profit=${profit:.2f}\n"
    f"roi_percent={roi:.1f}%\n"
    f"breakeven_sale_price=${breakeven_sale:.2f}\n"
  )
