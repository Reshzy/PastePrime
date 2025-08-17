"""
==============================================================

        ██████  ███████ ███████ ██   ██ ███████ ██    ██ 
        ██   ██ ██      ██      ██   ██    ███   ██  ██  
        ██████  █████   ███████ ███████   ███     ████   
        ██   ██ ██           ██ ██   ██  ███       ██    
        ██   ██ ███████ ███████ ██   ██ ███████    ██    
                                                              
                  Paste Prime – by Reshzy                     
==============================================================
"""

from typing import Optional
import threading
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import keyboard
except ImportError:
    keyboard = None

from cleaner import clean_text


class _ToolTip:
    def __init__(self, widget: tk.Widget, text: str, *, delay_ms: int = 400) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id = None
        self._tip_window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._on_enter, add=True)
        widget.bind("<Leave>", self._on_leave, add=True)
        widget.bind("<Motion>", self._on_motion, add=True)

    def _on_enter(self, _event=None) -> None:
        self._schedule()

    def _on_leave(self, _event=None) -> None:
        self._cancel()
        self._hide()

    def _on_motion(self, _event=None) -> None:
        # Restart timer on move to feel responsive
        self._cancel()
        self._schedule()

    def _schedule(self) -> None:
        if self._after_id is None:
            self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self) -> None:
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self) -> None:
        if self._tip_window is not None:
            return
        try:
            x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        except Exception:
            x, y, cx, cy = (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 16
        y = y + self.widget.winfo_rooty() + cy + 12
        tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        tip.attributes("-topmost", True)
        label = tk.Label(
            tip,
            text=self.text,
            justify=tk.LEFT,
            padx=8,
            pady=6,
            relief=tk.SOLID,
            borderwidth=1,
            bg="#FFFFE0",
        )
        label.pack()
        self._tip_window = tip

    def _hide(self) -> None:
        if self._tip_window is not None:
            try:
                self._tip_window.destroy()
            except Exception:
                pass
            self._tip_window = None


def add_tooltip(widget: tk.Widget, text: str) -> None:
    # Keep a reference on the widget to avoid garbage collection
    setattr(widget, "_tooltip", _ToolTip(widget, text))


class ClipboardCleanerApp(tk.Tk):
    """Simple desktop app to clean clipboard text for Warframe chat pasting."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Paste Prime")
        self.minsize(520, 360)

        # State
        self.auto_clean_enabled = tk.BooleanVar(value=True)
        self.ascii_only_enabled = tk.BooleanVar(value=False)
        self.last_seen_clipboard_text: Optional[str] = None
        self.is_setting_clipboard = False
        self.app_enabled = tk.BooleanVar(value=True)

        # Hotkey state
        self.hotkey_enabled = tk.BooleanVar(value=True)
        self.hotkey_var = tk.StringVar(value="ctrl+alt+v")
        self._typing_delay_ms = 500
        self._hotkey_id = None

        # Build UI
        self._build_ui()

        # Start polling clipboard
        self.after(300, self._poll_clipboard)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        # Options
        options_frame = ttk.LabelFrame(root, text="Options")
        options_frame.pack(fill=tk.X, pady=(0, 8))

        chk_auto = ttk.Checkbutton(
            options_frame,
            text="Auto-clean clipboard when it changes",
            variable=self.auto_clean_enabled,
        )
        chk_auto.pack(anchor=tk.W, pady=(4, 0))
        add_tooltip(chk_auto, "When enabled, the app cleans text automatically whenever you copy something new.")

        chk_ascii = ttk.Checkbutton(
            options_frame,
            text="Force ASCII (strip unsupported Unicode)",
            variable=self.ascii_only_enabled,
            command=self._update_preview_from_clipboard,
        )
        chk_ascii.pack(anchor=tk.W, pady=(4, 6))
        add_tooltip(chk_ascii, "Replace accented/Unicode characters with ASCII-only equivalents.")

        # Global hotkey controls
        hotkey_frame = ttk.Frame(options_frame)
        hotkey_frame.pack(fill=tk.X, pady=(0, 6))

        self.chk_hotkey = ttk.Checkbutton(
            hotkey_frame,
            text="Enable global hotkey to type from preview",
            variable=self.hotkey_enabled,
            command=self._update_hotkey_registration,
        )
        self.chk_hotkey.pack(anchor=tk.W)
        add_tooltip(self.chk_hotkey, "Allow a global keybind to type the cleaned preview text into the current window.")

        hotkey_row = ttk.Frame(options_frame)
        hotkey_row.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(hotkey_row, text="Hotkey:").pack(side=tk.LEFT)
        ent_hotkey = ttk.Entry(hotkey_row, textvariable=self.hotkey_var, width=18, state="readonly")
        ent_hotkey.pack(side=tk.LEFT, padx=(6, 0))
        btn_capture_hotkey = ttk.Button(hotkey_row, text="Change…", command=self._start_hotkey_capture)
        btn_capture_hotkey.pack(side=tk.LEFT, padx=(8, 0))
        add_tooltip(ent_hotkey, "The current global hotkey (read-only). Click Change… to set a new one.")
        add_tooltip(btn_capture_hotkey, "Click, then press the desired key combination (e.g., Ctrl+Alt+V).")

        # Buttons
        buttons_frame = ttk.Frame(root)
        buttons_frame.pack(fill=tk.X, pady=(0, 8))

        self.btn_clean_now = ttk.Button(buttons_frame, text="Clean & Copy", command=self._clean_clipboard_now)
        self.btn_clean_now.pack(side=tk.LEFT)
        add_tooltip(self.btn_clean_now, "Clean current clipboard text and copy the cleaned version back.")

        self.btn_type_preview = ttk.Button(buttons_frame, text="Type From Preview", command=self._type_from_preview)
        self.btn_type_preview.pack(side=tk.LEFT, padx=(8, 0))
        add_tooltip(self.btn_type_preview, "After a brief countdown, types the preview text into the active window.")

        self.btn_toggle_app = ttk.Button(buttons_frame, text="Disable App", command=self._toggle_app_enabled)
        self.btn_toggle_app.pack(side=tk.RIGHT)
        add_tooltip(self.btn_toggle_app, "Enable/Disable all features (auto-clean, hotkey, and actions).")

        # Preview
        preview_frame = ttk.LabelFrame(root, text="Preview (Cleaned)")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        add_tooltip(self.preview_text, "This shows what will be typed/copied. You can edit it here before using actions.")

        # Status bar
        status_frame = ttk.Frame(root)
        status_frame.pack(fill=tk.X, pady=(8, 0))

        self.status_var = tk.StringVar(value="Waiting for clipboard…")
        self.length_var = tk.StringVar(value="0 chars")

        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT)

        length_label = ttk.Label(status_frame, textvariable=self.length_var, anchor=tk.E)
        length_label.pack(side=tk.RIGHT)

        # Initialize preview from current clipboard
        self._update_preview_from_clipboard()
        # Register hotkey if enabled, then apply enabled/disabled state
        self._update_hotkey_registration()
        self._apply_enabled_state()

    def _poll_clipboard(self) -> None:
        """Poll the clipboard for changes and auto-clean if enabled."""
        try:
            if not self.app_enabled.get():
                self.status_var.set("App disabled")
                return
            if pyperclip is None:
                self.status_var.set("pyperclip not installed. Run: pip install -r requirements.txt")
                self.after(750, self._poll_clipboard)
                return

            current_text: Optional[str] = None
            try:
                current_text = pyperclip.paste()
            except Exception:
                # Non-text or clipboard unavailable
                pass

            if isinstance(current_text, str):
                if current_text != self.last_seen_clipboard_text:
                    self.last_seen_clipboard_text = current_text
                    if self.auto_clean_enabled.get():
                        cleaned = clean_text(current_text, ascii_only=self.ascii_only_enabled.get())
                        if cleaned != current_text:
                            self.is_setting_clipboard = True
                            try:
                                pyperclip.copy(cleaned)
                                self.status_var.set("Clipboard cleaned")
                                self.last_seen_clipboard_text = cleaned
                            finally:
                                # Delay flag reset to avoid racing with next poll
                                self.after(50, self._reset_setting_clipboard_flag)
                        else:
                            self.status_var.set("Clipboard already clean")
                    else:
                        self.status_var.set("Clipboard changed (auto-clean off)")
                    self._update_preview(cleaned_text_hint=None)
        finally:
            self.after(300, self._poll_clipboard)

    def _reset_setting_clipboard_flag(self) -> None:
        self.is_setting_clipboard = False

    def _clean_clipboard_now(self) -> None:
        if not self.app_enabled.get():
            self.status_var.set("App disabled")
            return
        if pyperclip is None:
            messagebox.showerror("Missing dependency", "pyperclip is not installed. Run: pip install -r requirements.txt")
            return
        try:
            original = pyperclip.paste()
        except Exception:
            original = ""
        if not isinstance(original, str) or original == "":
            self.status_var.set("Clipboard is empty or not text")
            self._update_preview(cleaned_text_hint="")
            return
        cleaned = clean_text(original, ascii_only=self.ascii_only_enabled.get())
        pyperclip.copy(cleaned)
        self.last_seen_clipboard_text = cleaned
        self.status_var.set("Clipboard cleaned (manual)")
        self._update_preview(cleaned_text_hint=cleaned)

    def _perform_typing(self, text: str) -> None:
        if not self.app_enabled.get():
            self.status_var.set("App disabled")
            return
        if pyautogui is None:
            messagebox.showerror("Missing dependency", "pyautogui is not installed. Run: pip install -r requirements.txt")
            return
        if not text:
            self.status_var.set("Nothing to type")
            return
        try:
            pyautogui.write(text, interval=0.005)
            self.status_var.set("Typed cleaned text")
        except Exception as e:
            messagebox.showerror("Typing failed", f"Could not send keystrokes: {e}")

    def _type_from_preview(self) -> None:
        if not self.app_enabled.get():
            self.status_var.set("App disabled")
            return
        if pyautogui is None:
            messagebox.showerror("Missing dependency", "pyautogui is not installed. Run: pip install -r requirements.txt")
            return
        text = self.preview_text.get("1.0", tk.END).rstrip("\n")
        if not text:
            self.status_var.set("Nothing to type")
            return

        # Small countdown dialog so the user can focus Warframe chat
        countdown_window = tk.Toplevel(self)
        countdown_window.title("Get Ready")
        countdown_window.resizable(False, False)
        ttk.Label(countdown_window, text="Switch to Warframe and focus chat. Typing begins in:").pack(padx=16, pady=(16, 4))
        counter_var = tk.StringVar(value="3")
        counter_label = ttk.Label(countdown_window, textvariable=counter_var, font=("Segoe UI", 18, "bold"))
        counter_label.pack(pady=(0, 12))

        def perform_typing() -> None:
            try:
                countdown_window.destroy()
            except Exception:
                pass
            self._perform_typing(text)

        def tick(count: int) -> None:
            if count <= 0:
                self.after(10, perform_typing)
                return
            counter_var.set(str(count))
            self.after(1000, lambda: tick(count - 1))

        # Center the countdown window relative to the main window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 100
        y = self.winfo_y() + (self.winfo_height() // 2) - 50
        countdown_window.geometry(f"200x120+{x}+{y}")

        tick(3)

    def _on_hotkey_triggered(self) -> None:
        # Called from a keyboard thread; marshal to Tk thread
        if not self.app_enabled.get():
            return
        text = self.preview_text.get("1.0", tk.END).rstrip("\n")
        self.after(self._typing_delay_ms, lambda: self._perform_typing(text))

    def _update_hotkey_registration(self) -> None:
        # Remove previous
        try:
            if self._hotkey_id is not None and keyboard is not None:
                keyboard.remove_hotkey(self._hotkey_id)
        except Exception:
            pass
        self._hotkey_id = None

        if not self.hotkey_enabled.get():
            self.status_var.set("Global hotkey disabled")
            return

        if keyboard is None:
            messagebox.showerror(
                "Missing dependency",
                "keyboard is not installed. Run: pip install -r requirements.txt (may require running as Administrator)",
            )
            self.hotkey_enabled.set(False)
            self.status_var.set("Global hotkey unavailable")
            return

        try:
            hotkey = (self.hotkey_var.get() or "ctrl+alt+v").strip()
            # Register and keep id to remove later
            self._hotkey_id = keyboard.add_hotkey(hotkey, lambda: self._on_hotkey_triggered())
            self.status_var.set(f"Global hotkey active: {hotkey}")
        except Exception as e:
            messagebox.showerror("Hotkey registration failed", f"Could not register hotkey: {e}")
            self.hotkey_enabled.set(False)
            self.status_var.set("Global hotkey unavailable")

    def _start_hotkey_capture(self) -> None:
        if keyboard is None:
            messagebox.showerror(
                "Missing dependency",
                "keyboard is not installed. Run: pip install -r requirements.txt (may require running as Administrator)",
            )
            return

        capture_win = tk.Toplevel(self)
        capture_win.title("Set Hotkey")
        capture_win.resizable(False, False)
        ttk.Label(capture_win, text="Press the desired hotkey combination\n(Press Esc to cancel)").pack(padx=16, pady=16)

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 140
        y = self.winfo_y() + (self.winfo_height() // 2) - 40
        capture_win.geometry(f"280x80+{x}+{y}")

        def capture_thread() -> None:
            combo: Optional[str] = None
            try:
                combo = keyboard.read_hotkey(suppress=False)
            except Exception:
                combo = None
            def finish() -> None:
                try:
                    capture_win.destroy()
                except Exception:
                    pass
                if combo and combo.lower() != "esc":
                    self.hotkey_var.set(combo)
                    self._update_hotkey_registration()
            self.after(0, finish)

        threading.Thread(target=capture_thread, daemon=True).start()

    def _apply_enabled_state(self) -> None:
        enabled = self.app_enabled.get()
        # Buttons
        self.btn_clean_now.configure(state=(tk.NORMAL if enabled else tk.DISABLED))
        self.btn_type_preview.configure(state=(tk.NORMAL if enabled else tk.DISABLED))
        # Hotkey registration
        if enabled:
            self._update_hotkey_registration()
            self.btn_toggle_app.configure(text="Disable App")
            if self.status_var.get() == "App disabled":
                self.status_var.set("Enabled")
        else:
            # Remove hotkey if present
            try:
                if self._hotkey_id is not None and keyboard is not None:
                    keyboard.remove_hotkey(self._hotkey_id)
            except Exception:
                pass
            self._hotkey_id = None
            self.btn_toggle_app.configure(text="Enable App")
            self.status_var.set("App disabled")

    def _toggle_app_enabled(self) -> None:
        self.app_enabled.set(not self.app_enabled.get())
        self._apply_enabled_state()

    def _update_preview_from_clipboard(self) -> None:
        if pyperclip is None:
            self._update_preview(cleaned_text_hint="")
            return
        try:
            clip = pyperclip.paste()
        except Exception:
            clip = ""
        if not isinstance(clip, str):
            clip = ""
        cleaned = clean_text(clip, ascii_only=self.ascii_only_enabled.get())
        self._update_preview(cleaned_text_hint=cleaned)

    def _update_preview(self, cleaned_text_hint: Optional[str]) -> None:
        if cleaned_text_hint is None:
            # Recompute from last seen
            source = self.last_seen_clipboard_text or ""
            cleaned_text_hint = clean_text(source, ascii_only=self.ascii_only_enabled.get())
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", cleaned_text_hint)
        self.length_var.set(f"{len(cleaned_text_hint)} chars")


def main() -> None:
    app = ClipboardCleanerApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()


