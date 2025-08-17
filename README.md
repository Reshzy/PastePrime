## Warframe Chat Paste (Paste Prime) (Windows)

Small desktop app that cleans copied messages (e.g., from warframe.market) so they paste reliably into Warframe in-game chat.

What it does:

- Removes zero-width and non-breaking spaces
- Replaces smart quotes/dashes/ellipsis with ASCII equivalents
- Normalizes Unicode and collapses whitespace
- Optional: force ASCII-only
- Auto-cleans clipboard whenever it changes (toggleable)
- Global hotkey to type the cleaned text into the focused window

### Requirements

- Windows with Python 3.9+

### Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

If PowerShell restricts scripts, you may need to run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Usage

1. Keep the app running.
2. Copy a message from your browser; the app auto-cleans the clipboard.
3. Paste in Warframe chat (Ctrl+V).
4. Use the "Force ASCII" option if the game rejects certain characters.
5. Alternatively, use the global hotkey (default: Ctrl+Alt+V) to type the cleaned text directly into the focused window, with a configurable delay.

The preview shows the cleaned text and character count. You can also click "Clean Clipboard Now" to manually clean current contents.

### Packaging (optional)

Create a standalone .exe with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name WarframePasteCleaner main.py
```

The executable will be in `dist/WarframePasteCleaner.exe`.

### Notes

- This app does not send keystrokes or automate gameplay; it only edits clipboard text.
- The "Type From Preview" and global hotkey features simulate typing the preview text into the current window. Keep the game chat focused before triggering.
- If you still cannot paste, ensure the message is not exceeding chat limits and that it contains only supported characters (enable ASCII-only).
- The `keyboard` package may require Administrator privileges to capture global hotkeys on some systems. If hotkey registration fails, run the app as Administrator or disable the hotkey.
