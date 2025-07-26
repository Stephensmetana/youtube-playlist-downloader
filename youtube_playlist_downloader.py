import os
import subprocess
import yt_dlp
from tqdm import tqdm

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

def get_playlist_entries(url):
    try:
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "dump_single_json": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                return [entry["url"] for entry in info["entries"]]
    except Exception as e:
        print(f"⚠️ Failed to get playlist info: {e}")
    return None

def download_video(url, download_path, audio_only):
    try:
        os.makedirs(download_path, exist_ok=True)
        command = [
            "yt-dlp",
            url,
            "-P", download_path
        ]
        if audio_only:
            command += [
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", "mp3"
            ]
        else:
            command += ["-f", "bestvideo+bestaudio/best"]

        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print(f"❌ Failed to download: {url}")

def download_with_progress(url, download_path, audio_only):
    if "list=" in url:
        video_urls = get_playlist_entries(url)
        if not video_urls:
            print("❌ Could not load playlist videos.")
            return
        print(f"\n📃 Playlist with {len(video_urls)} videos.")
        for video_url in tqdm(video_urls, desc="Downloading", unit="video"):
            download_video(video_url, download_path, audio_only)
        print("\n✅ Playlist download complete.\n")
    else:
        download_video(url, download_path, audio_only)
        print("✅ Download complete.\n")

# Main loop
while True:
    url = input("\nEnter YouTube video or playlist URL (or press Enter to quit): ").strip()
    if not url or not is_valid_url(url):
        break

    path = input("Enter download folder path: ").strip()
    if not os.path.isdir(path):
        print("❌ Invalid folder path. Try again.")
        continue

    mode = input("Download (v)ideo or (a)udio only? [v/a]: ").strip().lower()
    if mode not in ("v", "a"):
        print("❌ Invalid choice. Enter 'v' or 'a'.")
        continue

    audio_only = (mode == "a")
    download_with_progress(url, path, audio_only)
