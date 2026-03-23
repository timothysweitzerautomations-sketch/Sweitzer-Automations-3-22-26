Sweitzer Automations 3-22-26 — Mac & iPhone / iPad
==========================================

This folder contains an **Xcode** project that wraps the same **Revenue Pulse** and **Flip profit tracker**
HTML dashboards as the Windows and Android apps (`revenue_pulse/`).

What it does
------------

- **Build phase** “Copy revenue_pulse” copies `../../revenue_pulse/` into the app bundle next to resources
  (macOS: `Contents/Resources/`; iOS: inside the `.app` bundle).
- A **WKWebView** loads `app://localhost/revenue_pulse/index.html`.
- **`AppSchemeHandler`** (custom `WKURLSchemeHandler`) serves those files under the `app` scheme so
  relative links and `fetch()` for sample CSVs work (same idea as Android’s WebViewAssetLoader).
- Chart.js loads from the CDN — the app needs **network access** for charts (allowed by default for HTTPS).

Open in Xcode
-------------

1. Install **Xcode** from the Mac App Store (includes the iOS Simulator).
2. Open:

     apple/SweitzerAutomations/SweitzerAutomations.xcodeproj

3. In the toolbar, pick a run destination:
   - **My Mac** — native macOS window
   - **iPhone** or **iPad** simulator (or a plugged-in device)
4. **Signing & Capabilities**: for a real iPhone/iPad, select your **Team** in the target’s
   **Signing & Capabilities** tab (Personal Team is fine for your own devices).
5. Press **Run** (▶).

Command-line build (optional)
-----------------------------

From `apple/SweitzerAutomations`:

  xcodebuild -project SweitzerAutomations.xcodeproj -scheme SweitzerAutomations -configuration Debug \
    -destination 'platform=macOS,arch=arm64' build

Replace the destination with an iOS Simulator identifier from:

  xcodebuild -scheme SweitzerAutomations -showdestinations

Icons
-----

**AppIcon** lives in **Assets.xcassets** (iOS 1024 + macOS 512 @1x/@2x). Regenerate all platform icons from the repo root:

  python3 tools/generate_brand_icons.py

What’s not included
-------------------

Like the Android app, this does **not** include the Windows/Python **JSON sample report** windows —
only the web dashboards in the web view.

Desktop shortcut
----------------

**Sweitzer Automations 3-22-26 - Apple** on your Desktop points at this `apple` folder (update with
`bash scripts/setup_platform_apps.sh`). There is also **… - Project** (whole repo) and **… - Windows** / **… - Android**.
