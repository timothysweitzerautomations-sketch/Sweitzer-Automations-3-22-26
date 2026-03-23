# Build a Windows `.exe` for download

This packages **Revenue Pulse** and **Flip profit tracker** (the `revenue_pulse/` folder) into a single app users double-click. No command line.

## On a Windows PC (recommended)

1. Install [Python 3.11+](https://www.python.org/downloads/) (check **Add to PATH**).

2. Copy the **whole project** to the machine (or clone it).

3. Open **Command Prompt** in the project root (folder that contains `revenue_pulse/` and `windows_app/`).

4. Install PyInstaller:

   ```bat
   python -m pip install --upgrade pip
   python -m pip install pyinstaller
   ```

5. Build (run from project root) — either:

   **Option A — one click**

   ```bat
   windows\BUILD.bat
   ```

   or (same build, from project root):

   ```bat
   windows_app\build_exe.bat
   ```

   **Option B — manual**

   ```bat
   pyinstaller --noconfirm --onefile --windowed --name SweitzerAutomations-3-22-26 ^
     --paths . ^
     --add-data "revenue_pulse;revenue_pulse" ^
     --hidden-import=revenue_pulse ^
     --hidden-import=revenue_pulse.revenue_engine ^
     --hidden-import=revenue_pulse.flip_engine ^
     windows_app\launcher.py
   ```

   Add `--icon windows\icon.ico` (default in repo) or `--icon windows_app\icon.ico` if you use an override (see `README_ICON.txt`).

6. Share the file:

   `dist\SweitzerAutomations-3-22-26.exe`

Users double-click it: a window opens with:

- **Open Revenue Pulse** / **Open Flip profit tracker** — opens the browser to the local dashboards.
- **View flip sample (JSON)** / **View revenue sample (JSON)** — opens a second window with formatted sample output (and **Save as…** to export a `.json` file).

### Icon

The repo includes `windows\icon.ico`; builds pick it up automatically. To use your own icon, see `README_ICON.txt`.

## Notes

- First launch may trigger **Windows Defender SmartScreen** (“Unknown publisher”). You can [sign the exe](https://learn.microsoft.com/en-us/windows/win32/win_cert/wintrust) for production; for demos, users click “More info” → “Run anyway”.
- The app only serves **static files** + your CSV uploads in the browser; it does not need admin rights.
- **CrewAI / Ollama** (`main.py`) is not included in this exe — only the dashboards and sample CSVs.

## Test without building

From project root:

```bat
python windows_app\launcher.py
```
