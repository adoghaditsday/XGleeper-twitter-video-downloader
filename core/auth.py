from typing import List, Optional, Tuple

CookieCfg = Optional[Tuple[str, ...]]


def browser_cookie_candidates(choice: str) -> List[CookieCfg]:
    """
    Return yt-dlp cookiesfrombrowser candidates in fallback order.

    Supported explicit choices:
      - none
      - edge
      - firefox
      - chrome

    Auto fallback on Windows:
      Edge -> Chrome -> Firefox -> no cookies
    """
    choice = (choice or "Auto").strip().lower()

    if choice == "none":
        return [None]
    if choice == "edge":
        return [("edge",), None]
    if choice == "firefox":
        return [("firefox",), None]
    if choice == "chrome":
        return [("chrome",), None]

    return [
        ("edge",),
        ("chrome",),
        ("firefox",),
        None,
    ]
