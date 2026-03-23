Sweitzer Automations 3-22-26 — Android app
===================================

This folder is a small Android Studio project that wraps **Revenue Pulse** and the **Flip profit tracker**
(the same `revenue_pulse/` HTML dashboards as the Windows launcher).

What it does
------------

- On each build, Gradle copies `../revenue_pulse/` into `app/src/main/assets/revenue_pulse/`.
- The app opens a full-screen WebView on **Revenue Pulse** (`index.html`).
- Use the in-page link **Flip profit tracker →** to open the flip dashboard (same as on the web).
- **Load sample** buttons work: assets are served via `WebViewAssetLoader` (HTTPS to app assets) so `fetch()` can load the sample CSVs.
- Chart.js loads from the CDN — **Internet permission** is required for charts.

Requirements
------------

- [Android Studio](https://developer.android.com/studio) (recommended) with Android SDK (API 35) installed
- **Gradle 9.4** (via wrapper) supports running the build on **JDK 21+ including JDK 26** — no extra JDK install if your machine only has Java 26
- First open: let Gradle sync. If the SDK is not detected, copy `local.properties.example` to `local.properties` and set `sdk.dir` (see file comments).

Build
-----

From this `android` folder:

  macOS / Linux:   ./gradlew assembleDebug
  Windows:         gradlew.bat assembleDebug

Debug APK:

  app/build/outputs/apk/debug/app-debug.apk

Install on a device with USB debugging, or use **Run** in Android Studio.

Icons
-----

Launcher icons live under `app/src/main/res/mipmap-*` (same “S” style as the Windows icon).
Replace those PNGs if you want a custom look.

Desktop shortcut
----------------

**Sweitzer Automations 3-22-26 - Android** on your Desktop is an alias to this folder (create/update with `bash scripts/setup_platform_apps.sh`). Product name on device: **Sweitzer Automations 3-22-26**.

Note: the Python JSON sample viewers from the Windows launcher are not in this app — use the dashboards in the WebView only.
