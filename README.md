# YT Music Downloader (prosty)
# Free-Youtube-Downloader

Free open source youtube downloader without any limits :)

A small, standalone Python GUI application that downloads audio (and video) from YouTube links. The app uses `yt-dlp` for extraction and optionally `ffmpeg` for converting and merging streams.

Features
- Download audio in formats: `mp3`, `m4a`, `wav`.
- Download video (containers such as `mp4`, `webm`) and ensure Windows-compatible playback by transcoding video to H.264 + AAC when necessary.
- Choose output folder and bitrate (128k/192k/256k/320k).
- Displays video thumbnail and title before download.
- Uses a bundled `ffmpeg` if placed in `./ffmpeg/bin/ffmpeg.exe` (on Windows) or `./ffmpeg/ffmpeg` (on Unix).

Requirements
- Python 3.8+
- See `requirements.txt` (installs `yt-dlp`, `Pillow`, and `ttkbootstrap` if available)
- (Optional but recommended) `ffmpeg` for conversions and merging.

Installation
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

3. (Optional) Provide `ffmpeg`:
- Place `ffmpeg.exe` inside `ffmpeg\bin` in the project root (the app will automatically prefer it), or ensure `ffmpeg` is available on `PATH`.

Running
```powershell
python main.py
```

Usage
- Paste a YouTube link into the URL box and press `Search` to fetch title and thumbnail.
- Choose the desired format and bitrate.
- Optionally choose an output directory.
- Click `Download`.

Notes
- If `ffmpeg` is not available, the app will download the best available audio/video stream but will not convert containers. Placing `ffmpeg` in `./ffmpeg/bin` is the recommended way to bundle it with the app.
- For Windows playback compatibility, MP4 outputs are transcoded to H.264 video + AAC audio when needed.

License
This project is released under the MIT License. See the `LICENSE` file for details.

Contributing
- Contributions are welcome. Open an issue or submit a PR on the repository.

Repository
- Suggested repository name: `Free-Youtube-Downloader`
- Short description / tagline: "Free open source youtube downloader without any limits :)"
