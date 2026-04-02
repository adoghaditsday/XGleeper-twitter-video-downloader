import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk

from core.resolver import TwitterResolver
from core.downloader import TwitterDownloader
from core.utils import ensure_download_dir

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("XGleeper")
        self.geometry("860x600")
        self.minsize(780, 520)

        self.cookies_browser = "none"
        self.video_info = None
        self.format_map = {}
        self.output_dir = ensure_download_dir()

        self._build_ui()
        self._build_menu()
        self._refresh_backend_clients()

    def _build_menu(self):
        self.cookie_var = tk.StringVar(value=self.cookies_browser)

        menubar = tk.Menu(self)
        settings_menu = tk.Menu(menubar, tearoff=0)
        cookie_menu = tk.Menu(settings_menu, tearoff=0)

        for label, value in (
            ("None", "none"),
            ("Edge", "edge"),
            ("Firefox", "firefox"),
            ("Chrome", "chrome"),
        ):
            cookie_menu.add_radiobutton(
                label=label,
                value=value,
                variable=self.cookie_var,
                command=self._on_cookie_source_changed,
            )

        settings_menu.add_cascade(label="Cookie Source", menu=cookie_menu)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        self.config(menu=menubar)

    def _on_cookie_source_changed(self):
        self.cookies_browser = self.cookie_var.get()
        self._refresh_backend_clients()
        self.status_label.configure(text=f"Cookie source set to: {self.cookies_browser.capitalize()}")
        self.log(f"Cookie source changed to: {self.cookies_browser}")

    def _refresh_backend_clients(self):
        self.resolver = TwitterResolver(cookies_browser=self.cookies_browser)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Twitter/X Video Downloader", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste X/Twitter status URL here")
        self.url_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=0)

        self.fetch_button = ctk.CTkButton(self.button_frame, text="Fetch Formats", command=self.fetch_formats)
        self.fetch_button.grid(row=0, column=0, padx=(0, 10), pady=5)

        self.download_button = ctk.CTkButton(self.button_frame, text="Download Selected", command=self.download_selected)
        self.download_button.grid(row=0, column=1, padx=(0, 10), pady=5)

        self.folder_button = ctk.CTkButton(self.button_frame, text="Choose Folder", command=self.choose_folder)
        self.folder_button.grid(row=0, column=2, pady=5)

        self.info_box = ctk.CTkTextbox(self, height=160)
        self.info_box.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="nsew")

        self.format_label = ctk.CTkLabel(self, text="Available Formats")
        self.format_label.grid(row=4, column=0, padx=20, sticky="w")

        self.format_menu = ctk.CTkOptionMenu(self, values=["No formats loaded"])
        self.format_menu.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=6, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="w")

    def log(self, text: str):
        self.info_box.insert("end", text + "\n")
        self.info_box.see("end")

    def choose_folder(self):
        selected = filedialog.askdirectory(initialdir=str(self.output_dir))
        if selected:
            self.output_dir = Path(selected)
            self.status_label.configure(text=f"Output folder: {self.output_dir}")

    def _friendly_error(self, error: Exception) -> str:
        text = str(error)
        if "Could not copy Chrome cookie database" in text:
            return (
                "Chrome cookies could not be read. Close Chrome completely, including background "
                "processes, or switch the cookie source to Edge, Firefox, or None from Settings."
            )
        if "not a valid X/Twitter status URL" in text:
            return "Paste a direct x.com or twitter.com status URL."
        return text

    def fetch_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please paste a Twitter/X URL.")
            return

        self.fetch_button.configure(state="disabled")
        self.status_label.configure(text="Fetching metadata...")
        self.info_box.delete("1.0", "end")
        self.progress.set(0)
        self.log(f"Cookie source: {self.cookies_browser}")

        def worker():
            try:
                info = self.resolver.extract(url)
                self.video_info = info
                labels = []
                self.format_map.clear()

                for fmt in info["formats"]:
                    label = fmt.label
                    labels.append(label)
                    self.format_map[label] = fmt

                if not labels:
                    labels = ["No downloadable formats found"]

                self.after(0, self._update_formats, info, labels)
            except Exception as e:
                friendly = self._friendly_error(e)
                self.after(0, lambda: messagebox.showerror("Resolve Error", friendly))
                self.after(0, lambda: self.status_label.configure(text="Failed to fetch metadata."))
            finally:
                self.after(0, lambda: self.fetch_button.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def _update_formats(self, info, labels):
        self.format_menu.configure(values=labels)
        self.format_menu.set(labels[0])

        self.log(f"Title: {info['title']}")
        self.log(f"Uploader: {info.get('uploader')}")
        self.log(f"Page: {info.get('webpage_url')}")
        self.log(f"Raw formats found: {info.get('raw_format_count', 0)}")
        self.log(f"Filtered formats found: {len(info.get('formats', []))}")

        if not info.get('formats'):
            self.log("No usable downloadable formats survived filtering. Try switching Cookie Source to None for public posts.")
            self.status_label.configure(text="No formats found.")
        else:
            self.status_label.configure(text="Formats loaded.")

    def download_selected(self):
        url = self.url_entry.get().strip()
        selected = self.format_menu.get()

        if not url or not self.video_info:
            messagebox.showerror("Error", "Fetch a video first.")
            return

        fmt = self.format_map.get(selected)
        if not fmt:
            messagebox.showerror("Error", "Select a valid format.")
            return

        self.download_button.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="Starting download...")

        def update_progress(percent: float, text: str):
            self.after(0, lambda: self.progress.set(percent / 100.0))
            self.after(0, lambda: self.status_label.configure(text=text))

        def worker():
            try:
                downloader = TwitterDownloader(
                    cookies_browser=self.cookies_browser,
                    progress_callback=update_progress,
                )
                downloader.download(url, fmt.format_id, self.output_dir)
                self.after(0, lambda: messagebox.showinfo("Done", f"Saved to:\n{self.output_dir}"))
                self.after(0, lambda: self.status_label.configure(text="Download complete."))
            except Exception as e:
                friendly = self._friendly_error(e)
                self.after(0, lambda: messagebox.showerror("Download Error", friendly))
                self.after(0, lambda: self.status_label.configure(text="Download failed."))
            finally:
                self.after(0, lambda: self.download_button.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()
