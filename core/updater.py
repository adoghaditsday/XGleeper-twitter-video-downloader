from yt_dlp import version as yt_dlp_version


def get_local_yt_dlp_version() -> str:
    return getattr(yt_dlp_version, "__version__", "unknown")