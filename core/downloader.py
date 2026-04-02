from pathlib import Path
from typing import Callable, Optional

from yt_dlp import YoutubeDL

from .auth import browser_cookie_candidates
from .diagnostics import log_debug

ProgressCallback = Callable[[float, str], None]


class TwitterDownloader:
    def __init__(
        self,
        cookies_browser: str = "Auto",
        ffmpeg_path: str = "vendor",
        progress_callback: Optional[ProgressCallback] = None,
        verbose: bool = True,
    ) -> None:
        self.cookies_browser = cookies_browser
        self.ffmpeg_path = ffmpeg_path
        self.progress_callback = progress_callback
        self.verbose = verbose

    def _hook(self, data):
        if not self.progress_callback:
            return

        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            done = data.get("downloaded_bytes", 0)
            pct = (done / total * 100.0) if total else 0.0
            self.progress_callback(pct, f"Downloading... {pct:.1f}%")
        elif status == "finished":
            self.progress_callback(100.0, "Finishing...")

    def download(self, url: str, format_id: str, output_dir: Path):
        last_error = None

        for cookie_cfg in browser_cookie_candidates(self.cookies_browser):
            opts = {
                "format": format_id,
                "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
                "noplaylist": True,
                "ffmpeg_location": self.ffmpeg_path,
                "quiet": not self.verbose,
                "no_warnings": False,
                "progress_hooks": [self._hook],
                "merge_output_format": "mp4",
            }

            if cookie_cfg:
                opts["cookiesfrombrowser"] = cookie_cfg

            if self.verbose:
                opts["verbose"] = True

            try:
                browser_name = cookie_cfg[0] if cookie_cfg else "none"
                log_debug(f"Starting download with browser={browser_name} format_id={format_id}")
                with YoutubeDL(opts) as ydl:
                    ydl.download([url])
                return
            except Exception as e:
                last_error = e
                browser_name = cookie_cfg[0] if cookie_cfg else "none"
                log_debug(f"Download failed with browser={browser_name} error={e}")

        raise RuntimeError(f"Download failed. Last error: {last_error}")
