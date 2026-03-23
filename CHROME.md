# Chrome extension (companion)

This folder adds a **small toolbar extension** so you can open **Revenue Pulse** and **Flip profit tracker** in Chrome with one click.

## Why not bundle the full HTML inside the extension?

Chrome **Manifest V3** does not allow large **inline scripts** in extension pages (the same scripts that power `revenue_pulse/*.html`). Shipping those UIs unchanged would require splitting every script into separate files. Instead, this extension opens **the same local server** you already use:

```bash
python3 -m http.server 8765 --directory revenue_pulse
```

…or **`linux/serve_dashboards.sh`**, **`windows_app/launcher.py`**, etc. The extension only saves you from typing the URL.

## Install (developer / unpacked)

1. Start your local dashboard server (port **8765** by default, or pick another).
2. Open Chrome → **⋮** → **Extensions** → **Manage Extensions**.
3. Turn on **Developer mode** (top right).
4. **Load unpacked** → select the **`chrome_extension`** folder inside this repo  
   (`Sweitzer Automations 3-22-26/chrome_extension`).
5. Pin the extension if you like (**puzzle icon** → pin **Sweitzer Automations**).

## Use

1. Keep the **local server running** in a terminal.
2. Click the extension icon → **Revenue Pulse** or **Flip profit tracker**.
3. If nothing loads, check the port: extension **Options** (or right‑click extension → **Options**) and set the port to match your server (e.g. **9888**).

## Permissions

- **`http://127.0.0.1/*`** and **`http://localhost/*`** — open tabs to your machine only.
- **`storage`** — remember your port in **Options**.
- **`tabs`** — open a new tab to the dashboard URL.

## Publishing to Chrome Web Store (optional)

You would zip `chrome_extension/`, pay the developer fee, and submit. For personal use, **Load unpacked** is enough.

## Security note

This extension only talks to **localhost**. It does not send your data to a remote server; your CSVs stay in the browser session against your local `http.server`, same as opening the URL manually.
