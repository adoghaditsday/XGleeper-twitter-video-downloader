import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from yt_dlp import YoutubeDL

from .auth import browser_cookie_candidates
from .diagnostics import log_debug
from .models import VideoFormat


_STATUS_RE = re.compile(r"/(?:i/web|i)?/?status/(\d+)")
_ALLOWED_HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"}


class TwitterResolver:
    def __init__(self, cookies_browser: str = "none", ffmpeg_path: str = "vendor", verbose: bool = True) -> None:
        self.cookies_browser = cookies_browser
        self.ffmpeg_path = ffmpeg_path
        self.verbose = verbose

    def _validate_url(self, url: str) -> str:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        if host not in _ALLOWED_HOSTS:
            raise RuntimeError("Input is not a valid X/Twitter status URL")
        match = _STATUS_RE.search(parsed.path)
        if not match:
            raise RuntimeError("Input is not a valid X/Twitter status URL")
        return match.group(1)

    def _make_opts(self, cookie_cfg=None, strategy_idx: int = 1) -> Dict[str, Any]:
        opts: Dict[str, Any] = {
            "quiet": not self.verbose,
            "no_warnings": False,
            "noplaylist": True,
            "extract_flat": False,
            "ffmpeg_location": self.ffmpeg_path,
            "skip_download": True,
        }

        if cookie_cfg:
            opts["cookiesfrombrowser"] = cookie_cfg

        if strategy_idx == 2:
            opts["check_formats"] = False
        elif strategy_idx == 3:
            opts["http_headers"] = {"User-Agent": "Mozilla/5.0"}

        if self.verbose:
            opts["verbose"] = True

        return opts

    def _candidate_cookies(self) -> List[Optional[tuple]]:
        # Public X posts often work better without cookies first.
        base = [None]
        for item in browser_cookie_candidates(self.cookies_browser):
            if item not in base:
                base.append(item)
        return base

    def extract(self, url: str) -> Dict[str, Any]:
        tweet_id = self._validate_url(url)
        last_error: Optional[Exception] = None
        cookie_candidates = self._candidate_cookies()

        for cookie_cfg in cookie_candidates:
            for strategy_idx in (1, 2, 3):
                opts = self._make_opts(cookie_cfg=cookie_cfg, strategy_idx=strategy_idx)
                browser_name = cookie_cfg[0] if cookie_cfg else "none"
                try:
                    log_debug(f"Resolver try: tweet_id={tweet_id} browser={browser_name} strategy={strategy_idx} url={url}")
                    with YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=False)

                    raw_formats = info.get("formats", []) or []
                    formats = self._collect_formats(raw_formats)
                    log_debug(f"Resolver success: tweet_id={tweet_id} raw_formats={len(raw_formats)} filtered_formats={len(formats)} browser={browser_name}")

                    return {
                        "id": info.get("id"),
                        "tweet_id": tweet_id,
                        "title": info.get("title", "Untitled"),
                        "thumbnail": info.get("thumbnail"),
                        "webpage_url": info.get("webpage_url"),
                        "uploader": info.get("uploader"),
                        "duration": info.get("duration"),
                        "raw_format_count": len(raw_formats),
                        "formats": formats,
                        "raw_info": info,
                    }
                except Exception as e:
                    last_error = e
                    log_debug(f"Resolver failed: tweet_id={tweet_id} browser={browser_name} strategy={strategy_idx} error={e}")

        raise RuntimeError(f"Unable to extract media info. Last error: {last_error}")

    def _collect_formats(self, formats: List[Dict[str, Any]]) -> List[VideoFormat]:
        out: List[VideoFormat] = []
        seen = set()

        for fmt in formats:
            media_url = fmt.get("url")
            ext = fmt.get("ext")
            vcodec = fmt.get("vcodec")
            protocol = fmt.get("protocol")
            width = fmt.get("width")
            height = fmt.get("height")
            format_id = str(fmt.get("format_id", ""))

            if not media_url:
                continue
            if ext not in ("mp4", "m3u8", "webm"):
                continue
            if vcodec == "none" and fmt.get("acodec") != "none":
                continue

            key = (format_id, media_url, width, height, ext, protocol)
            if key in seen:
                continue
            seen.add(key)

            out.append(
                VideoFormat(
                    format_id=format_id,
                    ext=ext or "",
                    protocol=protocol,
                    width=width,
                    height=height,
                    fps=fmt.get("fps"),
                    filesize=fmt.get("filesize") or fmt.get("filesize_approx"),
                    vcodec=fmt.get("vcodec"),
                    acodec=fmt.get("acodec"),
                    url=media_url,
                    format_note=fmt.get("format_note"),
                    dynamic_range=fmt.get("dynamic_range"),
                )
            )

        out.sort(key=lambda f: ((f.height or 0), (f.width or 0), (f.filesize or 0)), reverse=True)
        return out
