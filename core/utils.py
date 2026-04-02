from pathlib import Path

def ensure_download_dir() -> Path:
    path = Path.home() / "Downloads" / "XGleeper"
    path.mkdir(parents=True, exist_ok=True)
    return path

def sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip() or "video"