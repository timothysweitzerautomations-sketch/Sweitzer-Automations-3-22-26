Icon for SweitzerAutomations-3-22-26.exe
================================

Default (in the repo)
---------------------

The project includes:

   windows\icon.ico

build_exe.bat uses it automatically when present.

Optional override
-----------------

1. Create or pick a square image (e.g. 256x256 PNG).
2. Convert it to .ico format (many free tools online: search "png to ico").
3. Save as either:

   windows\icon.ico          (replaces the default), or
   windows_app\icon.ico      (used only if windows\icon.ico is missing)

4. Run windows_app\build_exe.bat or windows\BUILD.bat again.

If no .ico is found, the exe uses the default Windows application icon.
