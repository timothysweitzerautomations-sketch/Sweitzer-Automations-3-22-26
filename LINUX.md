# Running on Linux

Copy or clone the **Sweitzer Automations 3-22-26** project. Same dashboards as Windows and macOS: **Revenue Pulse** and **Flip profit tracker** in `revenue_pulse/`.

## Option A — Desktop launcher (recommended, matches Windows)

Uses the same **Python + Tk** window as the Windows app (`windows_app/launcher.py`): buttons open the dashboards in your browser and show sample JSON.

### 1. Install Python and Tk

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install -y python3 python3-tk
```

**Fedora:**

```bash
sudo dnf install -y python3 python3-tkinter
```

**Arch:**

```bash
sudo pacman -S python tk
```

### 2. Run

From the **project root** (the folder that contains `linux/`, `revenue_pulse/`, `windows_app/`):

```bash
chmod +x linux/run_dashboards.sh
./linux/run_dashboards.sh
```

Or:

```bash
bash linux/run_dashboards.sh
```

---

## Option B — Browser only (no Tk)

If you do not install `python3-tk`, or you are on a **headless** machine, use a simple HTTP server and your browser:

```bash
chmod +x linux/serve_dashboards.sh
./linux/serve_dashboards.sh
```

Default URL: **http://127.0.0.1:8765/** — flip tracker: **http://127.0.0.1:8765/flip_tracker.html**

Another port:

```bash
PORT=9888 ./linux/serve_dashboards.sh
```

---

## CrewAI + Ollama (optional)

Same as other platforms: create a venv, install dependencies, run `main.py` with Ollama running. See the main **README.md**.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Ollama: https://ollama.com — then:
export PRODUCT="Example product"
export TARGET_PRICE="100"
python main.py
```

---

## Chart.js / CDN

The HTML dashboards load **Chart.js** from a public CDN. Your CSV data stays local; allow HTTPS outbound if you use a strict firewall.

---

## Chrome companion extension

After `serve_dashboards.sh` (or any local `http.server`) is running, you can use the **Chrome toolbar extension** in **`chrome_extension/`** to open the same URLs in one click. See **[CHROME.md](CHROME.md)**.

---

## Troubleshooting

| Issue | What to try |
|-------|----------------|
| `Tkinter not available` | Install `python3-tk` (Option A) or use Option B. |
| Port in use | `PORT=9888 ./linux/serve_dashboards.sh` |
| Browser does not open | Open the printed URL manually in Firefox/Chrome. |

---

## PyInstaller (optional, advanced)

You can package `windows_app/launcher.py` with PyInstaller on Linux for a single executable; paths differ from Windows (`:` vs `;` in `--add-data`). Most users run the shell scripts above instead.
