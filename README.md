<div align="center">
  <img src="assets/PastePrime.png" alt="Paste Prime Logo" width="200"/>
  
  # Paste Prime
  
  *A Warframe clipboard cleaner for seamless in-game chat pasting*
</div>

---

## Overview

Paste Prime is a lightweight desktop application that automatically cleans copied messages (e.g., from warframe.market) so they paste reliably into Warframe's in-game chat. It fixes the annoying bug where you can’t paste text inside the chat box — and since recent updates broke the old ‘display mode’ workaround, Paste Prime makes sure your trades and messages go through smoothly every time.

### ✨ Features

- **Auto-Clean Clipboard**: Automatically processes clipboard content when it changes
- **Smart Character Replacement**: Removes zero-width spaces, smart quotes, and other problematic characters
- **Global Hotkey**: Type cleaned text directly into any focused window (default: `Ctrl+Alt+V`)
- **ASCII-Only Mode**: Force conversion to ASCII characters for maximum compatibility
- **Real-time Preview**: See exactly what will be pasted with character count
- **Manual Control**: Clean clipboard on-demand or disable auto-cleaning
- **Custom Icon**: Beautiful Warframe-themed interface

## 🚀 Quick Start

### Option 1: Download Executable (Recommended)

1. Download the latest `PastePrime.exe` from the [Releases](../../releases) page
2. Run the executable - no installation required!

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/Reshzy/PastePrime.git
cd PastePrime

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

> **Note**: If PowerShell restricts script execution, run as Administrator and execute:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

## 📋 Requirements

- **Windows 10/11** (64-bit)
- **Python 3.9+** (only if running from source)

## 🎮 How to Use

1. **Launch Paste Prime** and keep it running in the background
2. **Copy text** from warframe.market, Discord, or anywhere else
3. **Paste in Warframe chat** (`Ctrl+V`) - the text is automatically cleaned!

### Advanced Features

- **Global Hotkey**: Press `Ctrl+Alt+V` to type cleaned text into the focused window
- **ASCII Mode**: Enable "Force ASCII" for games that reject Unicode characters
- **Manual Cleaning**: Use "Clean & Copy" button to process current clipboard content
- **Preview Editing**: Modify the cleaned text in the preview area before pasting

## ⚙️ Configuration Options

| Option               | Description                                           |
| -------------------- | ----------------------------------------------------- |
| Auto-clean clipboard | Automatically process clipboard when it changes       |
| Force ASCII          | Convert Unicode characters to ASCII equivalents       |
| Global hotkey        | Enable/disable and customize the global typing hotkey |
| App enable/disable   | Toggle all features on/off                            |

## 🛠️ Building from Source

To create your own executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable using the spec file
pyinstaller --noconfirm PastePrime.spec
```

The executable will be created in `dist/PastePrime.exe`.

## 🔧 Troubleshooting

### Common Issues

- **Hotkey not working**: Try running as Administrator or disable the hotkey feature
- **Still can't paste**: Enable "Force ASCII" mode or check Warframe's character limits
- **App won't start**: Ensure all dependencies are installed (`pip install -r requirements.txt`)

### Character Cleaning Process

Paste Prime removes/replaces:

- Zero-width spaces and non-breaking spaces
- Smart quotes (`"` `"` → `"`)
- Em/en dashes (`—` `–` → `-`)
- Ellipsis (`…` → `...`)
- Other problematic Unicode characters

## 📝 Notes

- This app **does not automate gameplay** - it only processes clipboard text
- The typing feature simulates keyboard input to the focused window
- Keep Warframe chat focused when using the global hotkey
- Some antivirus software may flag the executable - this is a false positive due to PyInstaller packaging

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source. Feel free to use, modify, and distribute as needed.

---

<div align="center">
  <strong>Happy trading, Tenno! 🎯</strong>
</div>
