import json
from pathlib import Path

SETTINGS_PATH = Path("data/settings.json")


DEFAULT_SETTINGS = {
    "appearance_mode": "dark",
    "download_dir": "",
    "cookies_browser": "Auto",   # Auto, Chrome, Edge, Firefox, None
    "verbose_debug": True,
    "ffmpeg_path": "vendor",
}


def load_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        return {**DEFAULT_SETTINGS, **json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))}
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")