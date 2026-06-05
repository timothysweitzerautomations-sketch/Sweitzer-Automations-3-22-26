Resume Pro AI — Android app
===========================

This folder is a small Android Studio project that wraps the bundled **Resume Pro AI**
HTML prototype from `../resume_pro/`.

What it does
------------

- On each build, Gradle copies `../resume_pro/` into `app/src/main/assets/resume_pro/`.
- The app opens a full-screen WebView on **Resume Pro AI** (`index.html`).
- The prototype includes guided flows for resume drafts, cover letters, resume bullet rewrites,
  interview answers, local saved documents, and a placeholder upgrade plan.
- Draft generation is currently local and template-driven. A real AI API/server and Google Play
  Billing can be connected in a later milestone.

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

Launcher icons live under `app/src/main/res/mipmap-*` (currently inherited from the previous app).
Replace those PNGs if you want a custom look.

Desktop shortcut
----------------

**Sweitzer Automations 3-22-26 - Android** on your Desktop is an alias to this folder
(create/update with `bash scripts/setup_platform_apps.sh`). Product name on device:
**Resume Pro AI**.
