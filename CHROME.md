# Chrome extension

The **`chrome_extension/`** folder is an **unpacked Manifest V3** extension. It opens the local **Revenue Pulse**, **Flip profit tracker**, and **Infotainment video player** UIs from the same `revenue_pulse/` source files.

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

Start the local dashboard server before using the toolbar buttons, or change the port in extension options.

## Use

1. Click the extension icon → **Revenue Pulse**, **Flip profit tracker**, or **Infotainment video player**.
2. A new tab opens to your local server, for example `http://127.0.0.1:8765/video_player.html`.
3. **Load sample** fetches the packaged `sample_sales.csv` / `sample_flips.csv`. Use **Choose file** for your own CSVs, or **Choose videos** for local video playback.

## Keeping the copy in sync

After you edit files under **`revenue_pulse/`** in the repo, refresh the extension’s copy:

```bash
bash scripts/sync_chrome_extension.sh
```

Then **Reload** the extension on the Extensions page.

## Local server

Run the shared UI server:

```bash
python3 -m http.server 8765 --directory revenue_pulse
```

…then click the extension buttons or open `http://127.0.0.1:8765/` in a normal tab.

## Permissions

- **`tabs`** — open a new tab to the local dashboard URL.

## Publishing to Chrome Web Store (optional)

Zip `chrome_extension/`, pay the developer fee, and submit. For personal use, **Load unpacked** is enough.

## Security note

CSV and video files you load stay in your browser session unless you export or upload them elsewhere.
