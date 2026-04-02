from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoFormat:
    format_id: str
    ext: str
    protocol: Optional[str]
    width: Optional[int]
    height: Optional[int]
    fps: Optional[float]
    filesize: Optional[int]
    vcodec: Optional[str]
    acodec: Optional[str]
    url: Optional[str]
    format_note: Optional[str]
    dynamic_range: Optional[str] = None

    @property
    def label(self) -> str:
        size = f"{self.width}x{self.height}" if self.width and self.height else "unknown-res"
        mb = f"{self.filesize / (1024 * 1024):.2f} MB" if self.filesize else "size unknown"
        proto = self.protocol or "?"
        return f"{size} | {self.ext} | {proto} | {mb} | {self.format_id}"