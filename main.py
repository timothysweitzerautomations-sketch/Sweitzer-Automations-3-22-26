import os
from pathlib import Path
from datetime import datetime

# Requires: `python -m pip install pyyaml` in your venv
import yaml

# CrewAI writes a SQLite DB via `appdirs.user_data_dir(...)` (macOS Library folder).
# In some environments (like this sandbox), that location isn't writable.
# Force appdirs to use a project-local data directory instead.
project_data_dir = Path(__file__).resolve().parent / ".data"
project_data_dir.mkdir(parents=True, exist_ok=True)
try:
  import appdirs  # type: ignore

  appdirs.user_data_dir = lambda *_args, **_kwargs: str(project_data_dir)  # type: ignore[assignment]
except Exception:
  # If appdirs isn't available yet, CrewAI will import it; on macOS that default path
  # may still be writable outside of sandboxed environments.
  pass

# Disable tracing/telemetry prompts (they can block execution in non-interactive shells).
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("CREWAI_TESTING", "true")
# LiteLLM uses tiktoken for token counting. Ensure it has a writable cache dir.
os.environ.setdefault(
  "CUSTOM_TIKTOKEN_CACHE_DIR",
  str((Path(__file__).resolve().parent / ".data" / "tiktoken_cache")),
)

from crewai import Agent, Task, Crew, Process, LLM  # noqa: E402

from tools.custom_tool import ddg_search, fee_calculator, scrape_website  # noqa: E402

def _load_yaml(path: Path) -> dict:
  return yaml.safe_load(path.read_text()) or {}


def build_crew() -> Crew:
  base = Path(__file__).resolve().parent
  agents_cfg = _load_yaml(base / "config" / "agents.yaml")
  tasks_cfg = _load_yaml(base / "config" / "tasks.yaml")
  (base / "outputs").mkdir(parents=True, exist_ok=True)

  llm_cfg = agents_cfg.get("llm", {})
  local_llm = LLM(
    model=llm_cfg.get("model", "ollama/llama3"),
    base_url=llm_cfg.get("base_url", "http://localhost:11434"),
  )

  tool_registry = {
    "ddg_search": ddg_search,
    "fee_calculator": fee_calculator,
    "scrape_website": scrape_website,
  }

  agents_by_id: dict[str, Agent] = {}
  for a in agents_cfg.get("agents", []):
    tools = [tool_registry[name] for name in a.get("tools", [])]
    agents_by_id[a["id"]] = Agent(
      role=a["role"],
      goal=a["goal"],
      backstory=a["backstory"],
      tools=tools,
      llm=local_llm,
    )

  tasks: list[Task] = []
  for t in tasks_cfg.get("tasks", []):
    agent = agents_by_id[t["agent_id"]]
    output_file = t.get("output_file")
    tasks.append(
      Task(
        description=t["description"],
        agent=agent,
        expected_output=t["expected_output"],
        output_file=output_file,
      )
    )

  return Crew(
    agents=list(agents_by_id.values()),
    tasks=tasks,
    process=Process.sequential,
  )

if __name__ == "__main__":
  crew = build_crew()
  product = os.getenv("PRODUCT", "Sony WH-1000XM5")
  target_price = os.getenv("TARGET_PRICE", "200")
  min_profit = os.getenv("MIN_PROFIT", "50")
  min_roi_percent = os.getenv("MIN_ROI_PERCENT", "30")

  result = crew.kickoff(
    inputs={
      "product": product,
      "target_price": target_price,
      "min_profit": min_profit,
      "min_roi_percent": min_roi_percent,
    }
  )
  print(result.raw)

  outputs_dir = Path(__file__).resolve().parent / "outputs"
  outputs_dir.mkdir(parents=True, exist_ok=True)
  safe_product = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in product)[:80]
  ts = datetime.now().strftime("%Y%m%d-%H%M%S")
  out_path = outputs_dir / f"{ts}_{safe_product}_buy{target_price}.txt"
  out_path.write_text(result.raw or "")
  