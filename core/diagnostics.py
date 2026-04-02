from datetime import datetime
from pathlib import Path

LOG_PATH = Path("data/debug.log")


def log_debug(message: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)