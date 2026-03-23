# Running on Windows

Copy the whole **Sweitzer Automations 3-22-26** project folder to your PC (USB, cloud, or zip).

## Downloadable app (`.exe`) for clients

Build a **double-click installer-style app** (no terminal) that opens a small window and launches the dashboards in the browser.

1. On a Windows machine with Python, open the project folder.
2. Follow **`windows_app/README_BUILD.md`** — one PyInstaller command produces `dist\SweitzerAutomations-3-22-26.exe`.
3. Zip that file (or your whole `dist` folder) and share it for download.

End users only run the `.exe` (they may need to allow it past SmartScreen the first time). The app window also has **View flip sample (JSON)** and **View revenue sample (JSON)** with optional **Save as…** — no command line needed.

---

## 1. Install Python

1. Download **Python 3.10+** from [python.org/downloads](https://www.python.org/downloads/windows/).
2. Run the installer.
3. Enable **“Add python.exe to PATH”** (or **Add Python to environment variables**).
4. Finish the install.

Open **Command Prompt** or **PowerShell** and check:

```bat
python --version
```

If that fails, try:

```bat
py --version
```

The scripts below try `py -3` first, then `python`.

## 2. Dashboard (Revenue Pulse + Flip tracker)

Double-click:

`scripts\windows\serve_dashboard.bat`

Or from the **project root** in a terminal:

```bat
cd path\to\Sweitzer_Automations
python -m http.server 8080 --directory revenue_pulse
```

Then in your browser:

- [http://localhost:8080/index.html](http://localhost:8080/index.html) — Revenue Pulse  
- [http://localhost:8080/flip_tracker.html](http://localhost:8080/flip_tracker.html) — Flip profit tracker  

Use **Load sample data** / **Load sample flips**, or upload your own CSV.

## 3. Command-line JSON (optional)

From the project root:

**Flip sample:**

```bat
scripts\windows\run_flip_sample.bat
```

**Revenue sample:**

```bat
scripts\windows\run_revenue_sample.bat
```

## 4. CrewAI + Ollama (optional, advanced)

The `main.py` agent flow needs a **virtual environment**, dependencies, and **Ollama** (or another LLM). That setup is heavier; start with the dashboard and CSV tools above. On Windows, use `python -m venv .venv` and `pip install` from your lockfile or docs when you are ready.

## 5. No extra pip for dashboards

The **Revenue Pulse** and **Flip** engines use **Python’s standard library** only. The batch files do **not** require `pip install` for those features.
