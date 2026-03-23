Sweitzer Automations 3-22-26 — Windows folder
=====================================

This folder holds the app icon and shortcuts for building and running the desktop launcher on Windows.

Files
-----

  icon.ico
      Multi-size icon used when you build SweitzerAutomations-3-22-26.exe (dark card with green accent + "S").

  BUILD.bat
      Double-click (or run from Command Prompt) to build dist\SweitzerAutomations-3-22-26.exe in the project root.
      Requires Python on PATH and installs PyInstaller automatically.

  RUN_LAUNCHER.bat
      Runs the launcher with Python without building an exe (good for testing).

Build details
-------------

Full instructions: ..\windows_app\README_BUILD.md

After a successful build, the executable is:

  ..\dist\SweitzerAutomations-3-22-26.exe

You can copy that file anywhere; keep icon.ico here when rebuilding so the exe keeps the same look.

Desktop shortcut (Mac)
------------------------

**Sweitzer Automations 3-22-26 - Windows** on your Desktop is an alias to this folder (see `bash scripts/setup_platform_apps.sh` in the repo root).
