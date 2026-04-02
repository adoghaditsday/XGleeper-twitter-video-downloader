"""
Paste this into your CustomTkinter/Tkinter main window file.
It adds a Settings menu with a Cookie Source submenu.

Expected behavior:
- self.cookies_browser stores the current selection
- self.resolver and self.downloader read from self.cookies_browser
"""

# In __init__ after creating the window:
self.cookies_browser = "None"  # or load from settings.json
self._build_menu()


# Add these methods to your main window class:
def _build_menu(self):
    import tkinter as tk

    self.cookie_var = tk.StringVar(value=self.cookies_browser)

    menubar = tk.Menu(self)
    settings_menu = tk.Menu(menubar, tearoff=0)
    cookie_menu = tk.Menu(settings_menu, tearoff=0)

    for label in ("None", "Edge", "Firefox", "Chrome"):
        cookie_menu.add_radiobutton(
            label=label,
            variable=self.cookie_var,
            value=label,
            command=self._on_cookie_source_changed,
        )

    settings_menu.add_cascade(label="Cookie Source", menu=cookie_menu)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    self.config(menu=menubar)


def _on_cookie_source_changed(self):
    self.cookies_browser = self.cookie_var.get()

    # Optional status line update
    if hasattr(self, "status_label"):
        self.status_label.configure(text=f"Cookie source: {self.cookies_browser}")

    # Recreate resolver/downloader if your app stores them persistently
    # Example:
    # self.resolver = TwitterResolver(cookies_browser=self.cookies_browser, ffmpeg_path="vendor", verbose=True)


# Wherever you instantiate the resolver/downloader, pass the selected source:
# resolver = TwitterResolver(cookies_browser=self.cookies_browser, ffmpeg_path="vendor", verbose=True)
# downloader = TwitterDownloader(cookies_browser=self.cookies_browser, ffmpeg_path="vendor", progress_callback=cb, verbose=True)
