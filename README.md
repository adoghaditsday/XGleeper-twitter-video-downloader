<img width="128" height="128" alt="gleeperico1" src="https://github.com/user-attachments/assets/95e0d9eb-d0d4-4b73-b090-bc430816a141" />


# XGleeper-twitter-video-downloader
Desktop app for X/Twitter video downloads. Paste a public tweet/status URL, fetch available video formats, choose quality, and save the file locally. Includes cookie-source options (None, Edge, Firefox, Chrome) to improve access for authorized content and handles format selection inside a simple GUI.
<img width="902" height="592" alt="image" src="https://github.com/user-attachments/assets/52c7f086-3431-4355-a3d7-fb243699a940" />
Chrome Extension: https://chromewebstore.google.com/detail/xgleeper/hipeobgdfidloebljgpnfnapinfmnddg

# About the Program
We built it as a small desktop GUI around three main jobs:

accept an X/Twitter status URL
resolve the available media formats
download the selected format to disk

The app entry point is just app.py, which launches the App window.

#How the app is structured

The window code lives in main_window.py. That file creates the interface:

URL input box
Fetch Formats button
Download Selected button
folder chooser
format dropdown
progress bar
log box
status text
cookie source menu

That is the visible shell of the app.

there are two backend pieces:

TwitterResolver in core/resolver.py
TwitterDownloader in core/downloader.py

The UI calls the resolver first, then the downloader second.

# “Fetch Formats”

fetch_formats() in the window code:

reads the URL from the entry box
clears old state
disables the fetch button
starts a background thread
calls self.resolver.extract(url) inside that thread

# "The resolver"
checks the X/Twitter URL
asks yt-dlp to inspect the page without downloading
collects the raw format data
filters it down into usable video entries
returns a dictionary with title, uploader, page URL, raw format count, and filtered formats

# “Download Selected”

download_selected():

checks that a URL was fetched already
checks that the chosen dropdown item maps to a real format
starts another background thread
creates TwitterDownloader
calls downloader.download(url, fmt.format_id, self.output_dir)

The downloader passes the selected format_id into yt-dlp, which performs the actual file retrieval and writes to the chosen folder. It also reports progress through a callback, which updates the progress bar and status text.

GUI layer handles user interaction
resolver layer discovers what media formats exist
downloader layer saves the chosen media file

The Settings → Cookie Source menu changes self.cookies_browser, then rebuilds the resolver with that setting. That means future fetches and downloads can try:

none
edge
firefox
chrome

The log box is your live trace of what the app is doing:

cookie source
title
uploader
page URL
raw formats found
filtered formats found
validation messages
download completion

<img width="1400" height="560" alt="xgleeper_promo-export2" src="https://github.com/user-attachments/assets/c1cdd3ad-c104-4322-89ce-548143656f1e" />
