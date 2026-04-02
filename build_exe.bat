@echo off
pyinstaller --noconfirm --clean --windowed --name TwitterVideoDownloader --icon assets\app.ico app.py
pause