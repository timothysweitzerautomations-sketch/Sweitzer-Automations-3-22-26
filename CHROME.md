# Chrome extension

The **`chrome_extension/`** folder is an **unpacked Manifest V3** extension. It ships the full **Revenue Pulse** and **Flip profit tracker** UIs (same HTML/JS as `revenue_pulse/`, with Chart.js vendored under `revenue_pulse/vendor/` so Chrome’s extension CSP allows the scripts).

## Install (developer / unpacked)

1. From the repo root, sync dashboards into the extension (first clone and after any edit under `revenue_pulse/`):

   ```bash
   bash scripts/sync_chrome_extension.sh
   ```

2. Open Chrome → **⋮** → **Extensions** → **Manage Extensions**.
3. Turn on **Developer mode** (top right).
4. **Load unpacked** → select the **`chrome_extension`** folder inside this repo  
   (`Sweitzer Automations 3-22-26/chrome_extension`).
5. Pin the extension if you like (**puzzle icon** → pin **Sweitzer Automations**).

No local `http.server` is required for the bundled dashboards.

## Use

1. Click the extension icon → **Revenue Pulse** or **Flip profit tracker**.
2. A new tab opens to `chrome-extension://…/revenue_pulse/index.html` or `…/flip_tracker.html`.
3. **Load sample** fetches the packaged `sample_sales.csv` / `sample_flips.csv`. Use **Choose file** for your own CSVs as before.

## Keeping the copy in sync

After you edit files under **`revenue_pulse/`** in the repo, refresh the extension’s copy:

```bash
bash scripts/sync_chrome_extension.sh
```

Then **Reload** the extension on the Extensions page.

## Why external JS and a local Chart bundle?

Chrome **Manifest V3** blocks **inline scripts** in extension pages. The dashboards were refactored so logic lives in **`index.js`** / **`flip_tracker.js`**, and Chart.js is loaded from **`vendor/chart.umd.min.js`** (not a CDN), matching extension **Content Security Policy**.

## Optional: same UI via local server

For development parity without reloading the extension:

```bash
python3 -m http.server 8765 --directory revenue_pulse
```

…then open `http://127.0.0.1:8765/` in a normal tab.

## Permissions

- **`tabs`** — open a new tab to the packaged dashboard URL.

## Publishing to Chrome Web Store (optional)

Zip `chrome_extension/` (including `revenue_pulse/` and `vendor/`), pay the developer fee, and submit. For personal use, **Load unpacked** is enough.

## Security note

The bundled pages run entirely inside the extension origin. CSV data you load stays in your browser session unless you export or upload it elsewhere.
