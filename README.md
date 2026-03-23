# Sweitzer Automations 3-22-26

**Cursor workspace:** open this folder in Cursor (File → Open Folder):

`/Users/timothysweitzer/Sweitzer Automations 3-22-26`

**GitHub (public source of truth):** [github.com/timothysweitzerautomations-sketch/Sweitzer-Automations-3-22-26](https://github.com/timothysweitzerautomations-sketch/Sweitzer-Automations-3-22-26)

This directory is the **full** project: `main.py`, `config/`, `tools/`, `revenue_pulse/`, and git history.

**CI (GitHub Actions):** on push/PR to `main` or `master`, [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs:

| Job | What it checks |
|-----|----------------|
| **test** | `pytest`, `build_crew()` smoke test |
| **android** | `./gradlew assembleDebug` (Ubuntu + Android SDK) |
| **xcode** | `xcodebuild` for macOS (`CODE_SIGNING_ALLOWED=NO`) |
| **windows_exe** | PyInstaller → `SweitzerAutomations-3-22-26.exe` |
| **chrome_extension** | Unpacked MV3 companion — [CHROME.md](CHROME.md) (opens local dashboard URLs) |

**Local (optional):** `bash scripts/verify_local_platforms.sh` — runs `demo_video_ready.sh` plus Android/Xcode **only if** the Android SDK and full **Xcode** (not only Command Line Tools) are installed. Windows `.exe` still needs a Windows machine or CI.

**Platform dashboards (same UI as the browser):** **`windows/`** (build a `.exe` via [`windows_app/README_BUILD.md`](windows_app/README_BUILD.md)), **`android/`** (Gradle / Android Studio), **`apple/`** (Xcode — Mac, iPhone, iPad), **`linux/`** ([LINUX.md](LINUX.md) — Tk launcher or browser-only server), **`chrome_extension/`** ([CHROME.md](CHROME.md) — Chrome toolbar companion to local server). Batch and shell helpers: [WINDOWS.md](WINDOWS.md), `scripts/windows/*.bat`.

**macOS setup (optional):** from the repo root, run **`bash scripts/setup_platform_apps.sh`** — creates Desktop aliases **`Sweitzer Automations 3-22-26 - Project`** (whole repo), **`… - Windows`**, **`… - Android`**, **`… - Apple`**, regenerates shared launcher icons (`tools/generate_brand_icons.py`), and writes **`android/local.properties`** if `~/Library/Android/sdk` exists. Re-run after moving the project folder.

| Where | What to open / run |
|-------|---------------------|
| Windows PC | `windows\BUILD.bat` or `windows_app\build_exe.bat` → `dist\SweitzerAutomations-3-22-26.exe` |
| Linux | [LINUX.md](LINUX.md) — `./linux/run_dashboards.sh` (GUI) or `./linux/serve_dashboards.sh` (browser only) |
| Chrome | [CHROME.md](CHROME.md) — load unpacked `chrome_extension/`; local server must be running |
| Android | `android/README.txt` — `./gradlew assembleDebug` or Android Studio |
| Mac / iPhone / iPad | `apple/README.txt` — `SweitzerAutomations.xcodeproj` |

Two capabilities live in this repo:

## 1. CrewAI resale / arbitrage workflow

Finds comps, estimates profit with marketplace fees, and outputs a BUY/PASS report using a local LLM (Ollama).

- **Run:** from this directory, with Ollama up and a model pulled:

  ```bash
  source .venv/bin/activate
  export PRODUCT="Sony WH-1000XM5"
  export TARGET_PRICE="200"
  python main.py
  ```

- **Optional env:** `SAMPLE_SALES_CSV` and `FLIP_CSV` — paths passed into tasks for `sales_csv_summary` / `flip_csv_summary` (defaults: `revenue_pulse/sample_sales.csv`, `revenue_pulse/sample_flips.csv`).
- **Config:** `config/agents.yaml`, `config/tasks.yaml`
- **Outputs:** `outputs/` (and task `output_file` targets)

**Batch runs (multiple products):** `manifest.csv` lists `product`, `target_price`, `min_profit`, `min_roi_percent`. Run:

```bash
source .venv/bin/activate
python manifest_runner.py
```

Override the file with `MANIFEST=/path/to/manifest.full.csv` (see `manifest.full.csv` for a two-row example).

### Tools

| Tool | Purpose |
|------|---------|
| `ddg_search` | Web search for prices |
| `scrape_website` | Fetch page text |
| `fee_calculator` | Net profit, ROI, breakeven from sale/buy/fee/shipping |
| `sales_csv_summary` | JSON revenue summary from a sales CSV (see Revenue Pulse) |
| `flip_csv_summary` | JSON flip ledger: buy, sold price, fees, shipping → profit & ROI per row (see Flip tracker) |

The **Profit Analyst** agent can call `sales_csv_summary` or `flip_csv_summary` when tasks reference a CSV path (e.g. `revenue_pulse/sample_sales.csv`, `revenue_pulse/sample_flips.csv`).

## 2. Revenue Pulse (sales analytics)

Browser dashboard + stdlib Python engine for transaction CSVs.

- **Serve the UI:**

  ```bash
  python3 -m http.server 8080 --directory revenue_pulse
  ```

  Open `http://localhost:8080`, then **Choose CSV** or **Load sample data**.

- **CLI (same logic as the UI):**

  ```bash
  python3 -m revenue_pulse.revenue_engine revenue_pulse/sample_sales.csv
  ```

CSV expectations: header row; a column the app can treat as **transaction amount**. Recognized names include **`amount`**, **`revenue`**, **`total`**, **`payment`**, **`gross_sales`**, **`net_sales`**, **`line_total`**, **`payout`**, and similar (see `AMOUNT_ALIASES` in `revenue_pulse/revenue_engine.py`). Headers containing **`total`**, **`revenue`**, or **`amount`** are also matched. Rename your export’s money column if you see “no amount column found.” Optional: **date**, **product**, **customer**.

## 3. Flip profit tracker (resale / flipping)

**Sourcing vs actuals (like a serious sheet):**

- **`est_sale_price`** + optional **`est_fee_percent`**, **`est_shipping`**, **`est_packaging`**, **`est_mileage_cost`**, **`est_taxes`**, **`est_promotion_fees`** — snapshot when you buy / list (defaults: 15% fee if no `est_fee_percent`).
- **`sold_price`** + actual **`fee_percent`**, **`shipping_cost`**, **`taxes`**, **`promotion_fees`**, **`packaging_cost`**, **`mileage_cost`** — when the sale closes.
- Leave **`sold_price`** empty for **pending** inventory; we only sum **estimated** profit for those rows (by **`purchase_date`** month if present).
- When both estimate and actual exist on a row, JSON includes **`variance_estimate_vs_actual`** (actual profit minus estimated profit).

- **Same UI server as above.** Open `http://localhost:8080/flip_tracker.html` (or the link from Revenue Pulse).

- **CLI:**

  ```bash
  python3 -m revenue_pulse.flip_engine revenue_pulse/sample_flips.csv
  ```

**Not tax or legal advice.** General inventory / overhead lines (not per-sale) are still outside this file — only **per-line sale** economics here.

## Automated tests (pytest)

From the project root, with dev deps installed:

```bash
source .venv/bin/activate   # or your venv
pip install -r requirements-dev.txt
pytest tests/ -v
```

- `tests/test_revenue_engine.py` — `sample_sales.csv`
- `tests/test_flip_engine.py` — `sample_flips.csv`
- `tests/test_flip_ledger_tool.py` — CrewAI `flip_csv_summary` (skipped if `crewai` missing)

Add new files under `tests/` following the same pattern.

**Release check:** `bash scripts/demo_video_ready.sh` (Ollama + pytest + `build_crew`).

**Keep checks handy (Cursor / VS Code):** **Terminal → Run Task…** (or **⌘⇧B** / **Ctrl+Shift+B** for the default build task) → **Local checks: demo_video_ready**. Other tasks: **Pytest only**, **Serve Revenue Pulse (8080)** — see [`.vscode/tasks.json`](.vscode/tasks.json).

**Optional — shell alias** (add to `~/.zshrc`, then `source ~/.zshrc`):

`alias sweitzer-check='cd "/Users/timothysweitzer/Sweitzer Automations 3-22-26" && bash scripts/demo_video_ready.sh'`

## Research / notes

[`research/`](research/) — scratch notes and interview scripts; not required to run the app.

## Layout

- `main.py` — CrewAI entrypoint; registers tools for agents
- `config/` — `agents.yaml`, `tasks.yaml`
- `tools/` — `custom_tool.py`, `revenue_analytics.py`, `flip_ledger.py`
- `revenue_pulse/` — `index.html`, `flip_tracker.html`, `revenue_engine.py`, `flip_engine.py`, sample CSVs
- `tests/` — pytest suite; `requirements-dev.txt` — pytest only
- `docs/video/` — demo recording prep, Gemini handoff text, talking-point cue cards
- `linux/` — [LINUX.md](LINUX.md) user-friendly dashboard launchers
- `chrome_extension/` — [CHROME.md](CHROME.md) Chrome toolbar companion (localhost)
