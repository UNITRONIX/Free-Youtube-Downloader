import threading
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import urllib.request
import io
import tempfile

try:
    import yt_dlp as ytdl
except Exception:
    ytdl = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None
import threading
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import urllib.request
import io
import sys
import subprocess
import re

try:
    import yt_dlp as ytdl
except Exception:
    ytdl = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import DARK
except Exception:
    tb = None


class YTDownloaderApp:
    # Available audio formats and default
    FORMATS_AUDIO = ['mp3', 'm4a', 'wav']
    DEFAULT_FORMAT = 'mp3'

    def __init__(self, root):
        self.root = root
        root.title('Free-Youtube-Downloader')

        # main container
        pad = 12
        container = tk.Frame(root, bg='#1e1e1e')
        container.pack(fill='both', expand=True)

        # Top row: URL + Szukaj
        top = tk.Frame(container, bg='#1e1e1e')
        top.pack(fill='x', padx=pad, pady=(pad, 6))

        self.url_var = tk.StringVar()
        url_entry = tk.Entry(top, textvariable=self.url_var, font=('Segoe UI', 11), width=60, bg='#2b2b2b', fg='white', insertbackground='white')
        url_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))

        self.search_btn = tk.Button(top, text='Search', command=self.on_search, bg='#3a7bd5', fg='white')
        self.search_btn.pack(side='right')

        # Progress bar for info loading
        self.progress = None
        try:
            from tkinter import ttk
            self.progress = ttk.Progressbar(container, mode='indeterminate')
            self.progress.pack(fill='x', padx=pad, pady=(0, 8))
        except Exception:
            self.progress = None

        # Middle: thumbnail + title (title hidden until loaded)
        middle = tk.Frame(container, bg='#1e1e1e')
        middle.pack(fill='x', padx=pad, pady=(4, 4))

        self.thumb_label = tk.Label(middle, text='', bg='#1e1e1e')
        self.thumb_label.pack(side='left')

        self.title_var = tk.StringVar(value='')
        self.title_label = tk.Label(middle, textvariable=self.title_var, font=('Segoe UI', 12, 'bold'), fg='white', bg='#1e1e1e')
        self.title_label.pack(side='left', padx=(12, 0))
        self.title_label.pack_forget()

        self._thumbnail_image = None

        # Format selector (audio only)
        fmt_frame = tk.Frame(container, bg='#1e1e1e')
        fmt_frame.pack(fill='x', padx=pad, pady=(6, 6))

        self.format_var = tk.StringVar(value=self.DEFAULT_FORMAT)
        fmt_label = tk.Label(fmt_frame, text='Format:', fg='white', bg='#1e1e1e')
        fmt_label.pack(side='left')

        menu_btn = tk.Menubutton(fmt_frame, text='Choose format', relief='raised', bg='#2b2b2b', fg='white')
        menu = tk.Menu(menu_btn, tearoff=0)
        for f in self.FORMATS_AUDIO:
            menu.add_radiobutton(label=f, variable=self.format_var, value=f)
        menu_btn.config(menu=menu)
        menu_btn.pack(side='left', padx=(8, 0))

        # Bitrate selector
        self.bitrate_var = tk.StringVar(value='192k')
        br_label = tk.Label(fmt_frame, text='Bitrate:', fg='white', bg='#1e1e1e')
        br_label.pack(side='left', padx=(12, 0))
        bitrate_menu = tk.OptionMenu(fmt_frame, self.bitrate_var, '128k', '192k', '256k', '320k')
        bitrate_menu.config(bg='#2b2b2b', fg='white')
        bitrate_menu.pack(side='left', padx=(8, 0))

        # Actions: choose location + download
        actions = tk.Frame(container, bg='#1e1e1e')
        actions.pack(fill='x', padx=pad, pady=(6, pad))

        downloads_default = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.output_dir = tk.StringVar(value=downloads_default)
        choose_btn = tk.Button(actions, text='Choose location', command=self.choose_folder, bg='#2b2b2b', fg='white')
        choose_btn.pack(side='left')

        self.dir_label = tk.Label(actions, textvariable=self.output_dir, fg='white', bg='#1e1e1e')
        self.dir_label.pack(side='left', padx=(8, 0), expand=True, fill='x')

        self.download_btn = tk.Button(actions, text='Download', command=self.start_download, bg='#28a745', fg='white')
        self.download_btn.pack(side='right')

        # status bar
        self.status_var = tk.StringVar(value='Ready')
        status = tk.Label(root, textvariable=self.status_var, anchor='w', bg='#151515', fg='white')
        status.pack(fill='x')

    def choose_folder(self):
        d = filedialog.askdirectory(initialdir=self.output_dir.get())
        if d:
            self.output_dir.set(d)

    def on_search(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning('No URL', 'Please paste a YouTube link.')
            return
        if ytdl is None:
            messagebox.showerror('Missing library', 'yt-dlp is not installed.')
            return

        # start progress
        if self.progress:
            try:
                self.progress.start(10)
            except Exception:
                pass

        self.status_var.set('Fetching info...')
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            with ytdl.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get('title') or '-'
            thumbnail = info.get('thumbnail')

            # update UI
            def ui_update():
                self.title_var.set(title)
                self.title_label.pack(side='left', padx=(12, 0))
                if thumbnail and Image is not None and ImageTk is not None:
                    try:
                        data = urllib.request.urlopen(thumbnail, timeout=8).read()
                        im = Image.open(io.BytesIO(data))
                        im.thumbnail((160, 160))
                        self._thumbnail_image = ImageTk.PhotoImage(im)
                        self.thumb_label.config(image=self._thumbnail_image, text='')
                    except Exception:
                        self.thumb_label.config(text='(thumbnail unavailable)', fg='white')
                else:
                    self.thumb_label.config(text='(no thumbnail)', fg='white')
                self.status_var.set('Ready')
                if self.progress:
                    try:
                        self.progress.stop()
                    except Exception:
                        pass

            self.root.after(0, ui_update)

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set('Error fetching info: ' + str(e)))
            if self.progress:
                try:
                    self.progress.stop()
                except Exception:
                    pass

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning('No URL', 'Please paste a YouTube link.')
            return
        if ytdl is None:
            messagebox.showerror('Missing library', 'yt-dlp is not installed.')
            return

        self.download_btn.config(state='disabled')
        self.status_var.set('Starting download...')
        threading.Thread(target=self._download_thread, args=(url, self.output_dir.get(), self.format_var.get(), self.bitrate_var.get()), daemon=True).start()

    def _download_thread(self, url, outdir, wanted_format, wanted_bitrate):
        try:
            # get info first to know title and build deterministic filename
            info = None
            try:
                with ytdl.YoutubeDL({'quiet': True}) as ydl_info:
                    info = ydl_info.extract_info(url, download=False)
            except Exception:
                info = None

            def sanitize_name(name: str) -> str:
                # remove characters illegal in filenames on Windows
                return re.sub(r'[<>:"/\\|?*]', '_', name)

            title = (info.get('title') if info else None) or 'download'
            safe_title = sanitize_name(title)
            project_dir = os.path.dirname(os.path.abspath(__file__))

            # check common packaged ffmpeg locations first, then PATH
            exe_name = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
            cand1 = os.path.join(project_dir, 'ffmpeg', 'bin', exe_name)
            cand2 = os.path.join(project_dir, 'ffmpeg', exe_name)
            ffmpeg_exe = None
            if os.path.exists(cand1):
                ffmpeg_exe = cand1
            elif os.path.exists(cand2):
                ffmpeg_exe = cand2
            else:
                ffmpeg_exe = shutil.which('ffmpeg')

            ffmpeg_location = os.path.dirname(ffmpeg_exe) if ffmpeg_exe else None

            # Ensure project's ffmpeg dir is first in PATH so yt-dlp/subprocess use it
            if ffmpeg_location:
                cur_path = os.environ.get('PATH', '')
                if ffmpeg_location not in cur_path.split(os.pathsep):
                    os.environ['PATH'] = ffmpeg_location + os.pathsep + cur_path

            outtmpl = os.path.join(outdir, f'{safe_title}.%(ext)s')
            ydl_opts = {'outtmpl': outtmpl, 'noplaylist': True, 'quiet': True, 'progress_hooks': [self._progress_hook]}
            if ffmpeg_location:
                ydl_opts['ffmpeg_location'] = ffmpeg_location

            if wanted_format in ('mp3', 'm4a', 'wav'):
                ydl_opts['format'] = 'bestaudio/best'
                if ffmpeg_exe:
                    # yt-dlp preferredquality expects numeric bitrate (e.g. '192')
                    pref_q = wanted_bitrate.rstrip('k') if wanted_bitrate else '192'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio', 'preferredcodec': wanted_format, 'preferredquality': pref_q
                    }]

            else:
                # video
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
                # prefer ffmpeg and set merge format so yt-dlp merges video+audio
                ydl_opts['prefer_ffmpeg'] = True
                if wanted_format in ('mp4', 'webm'):
                    ydl_opts['merge_output_format'] = wanted_format

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # locate downloaded file(s) matching safe_title
            candidates = []
            for fn in os.listdir(outdir):
                if fn.startswith(safe_title + '.'):
                    candidates.append(os.path.join(outdir, fn))

            if not candidates:
                self.root.after(0, lambda: self.status_var.set('Downloaded but no file found.'))
            else:
                # pick largest file
                src = max(candidates, key=lambda p: os.path.getsize(p))
                src_ext = os.path.splitext(src)[1].lstrip('.')
                desired_ext = wanted_format

                # find ffmpeg executable
                ffmpeg_exe = None
                if ffmpeg_location:
                    exe = os.path.join(ffmpeg_location, 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
                    if os.path.exists(exe):
                        ffmpeg_exe = exe
                if ffmpeg_exe is None:
                    ffmpeg_exe = shutil.which('ffmpeg')

                if src_ext.lower() != desired_ext.lower():
                    if ffmpeg_exe:
                        dst = os.path.splitext(src)[0] + '.' + desired_ext
                        # build conversion command
                        cmd = [ffmpeg_exe, '-y', '-i', src]
                        if desired_ext in ('mp3', 'm4a', 'wav'):
                            # convert to audio-only formats (mp3/m4a/wav)
                            if desired_ext == 'mp3':
                                cmd += ['-vn', '-c:a', 'libmp3lame', '-b:a', '192k', dst]
                            elif desired_ext == 'm4a':
                                cmd += ['-vn', '-c:a', 'aac', '-b:a', '192k', dst]
                            else:  # wav
                                cmd += ['-vn', '-c:a', 'pcm_s16le', dst]
                        else:
                            # video container: copy video stream, convert audio to AAC for compatibility
                            if desired_ext == 'mp4':
                                # Transcode video to H.264 and audio to AAC for maximum Windows compatibility
                                cmd += ['-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-c:a', 'aac', '-b:a', '192k', dst]
                            elif desired_ext == 'webm':
                                # for webm keep streams where possible
                                cmd += ['-c', 'copy', dst]
                            else:
                                cmd += ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', dst]

                        try:
                            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            try:
                                os.remove(src)
                            except Exception:
                                pass
                            self.root.after(0, lambda: self.status_var.set(f'Saved as {os.path.basename(dst)}'))
                        except Exception as e:
                            self.root.after(0, lambda: self.status_var.set('Conversion failed: ' + str(e)))
                    else:
                        # no ffmpeg: if audio wanted and original contains audio-only, we can rename, but better inform user
                        self.root.after(0, lambda: self.status_var.set(f'Downloaded {os.path.basename(src)} (ffmpeg not available for conversion)'))
                else:
                    self.root.after(0, lambda: self.status_var.set('Download finished'))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set('Error: ' + str(e)))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state='normal'))

    def _progress_hook(self, d):
        status = d.get('status')
        if status == 'downloading':
            pct = d.get('_percent_str', '')
            sp = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            self.root.after(0, lambda: self.status_var.set(f'Downloading {pct} {sp} ETA {eta}'))
        elif status == 'finished':
            self.root.after(0, lambda: self.status_var.set('Processing...'))


def main():
    # prefer ttkbootstrap for modern dark theme when available
    if tb is not None:
        style = tb.Style('darkly')
        root = style.master
    else:
        root = tk.Tk()
        root.configure(bg='#1e1e1e')

    app = YTDownloaderApp(root)
    root.geometry('760x420')
    root.mainloop()


if __name__ == '__main__':
    main()
