AI Resume Builder - Android app
================================

This folder is an Android Studio project for the on-device AI Resume Builder Play app.
It wraps the static `resume_builder/` HTML and JavaScript UI in a full-screen WebView.

What it does
------------

- On each build, Gradle copies `../resume_builder/index.html` and `../resume_builder/app.js` into `app/src/main/assets/resume_builder/`.
- The app opens the resume builder at `https://appassets.androidplatform.net/assets/resume_builder/index.html`.
- Resume text, job descriptions, scoring, keyword-gap detection, and bullet suggestions run in local JavaScript.
- The release does not request Android Internet permission. Do not add network calls unless the Play Console Data safety answers and privacy policy are updated first.

Requirements
------------

- [Android Studio](https://developer.android.com/studio) with Android SDK API 35 installed
- Gradle wrapper included in this folder
- First open: let Gradle sync. If the SDK is not detected, copy `local.properties.example` to `local.properties` and set `sdk.dir` (see file comments).

Build
-----

From this `android` folder:

  macOS / Linux:   ./gradlew assembleDebug
  Windows:         gradlew.bat assembleDebug

Debug APK:

  app/build/outputs/apk/debug/app-debug.apk

For Google Play, create a signed Android App Bundle (`.aab`) from Android Studio or a release Gradle signing configuration.

Play Console notes
------------------

- Application ID: `com.sweitzer.resumebuilder`
- Device app name: `AI Resume Builder`
- Privacy posture for this build: on-device processing only; no resume text is transmitted by the app.
- See `../docs/google_play_resume_builder.md` before creating a production release, especially if you later add hosted AI, analytics, crash reporting, or ads.

Icons
-----

Launcher icons live under `app/src/main/res/mipmap-*`. Replace those PNGs with resume-builder-specific artwork before a public Play release.
