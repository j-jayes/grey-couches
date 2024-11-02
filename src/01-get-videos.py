"""
This file fetches video metadata from a YouTube playlist and saves it to a JSON file.
It also downloads the largest thumbnail for each video and saves it to a local folder.
"""

import yt_dlp
import json
import requests
from datetime import datetime
import os

# Define playlist URL and JSON file paths
playlist_url = "https://youtube.com/playlist?list=PL1WZky7MVeY_6H2ieeVKitXGd3npyPo-g&si=sNuLJYlNXl8a4XCs"
output_file = "data/never_too_small_official_playlist.json"
thumbnail_folder = "data/thumbnails"

# yt-dlp options for metadata extraction only
ydl_opts = {
    'quiet': True,
    'extract_flat': 'in_playlist',
    'skip_download': True
}

# Ensure thumbnail directory exists
os.makedirs(thumbnail_folder, exist_ok=True)

def fetch_playlist_videos(url):
    """Fetches all video metadata from the playlist."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        videos_data = []

        for entry in playlist_info['entries']:
            # Get largest thumbnail if available
            thumbnails = entry.get("thumbnails", [])
            if thumbnails:
                largest_thumbnail = max(thumbnails, key=lambda t: t["width"] * t["height"])
                thumbnail_url = largest_thumbnail["url"]
                thumbnail_path = os.path.join(thumbnail_folder, f"{entry['id']}.png")
                download_thumbnail(thumbnail_url, thumbnail_path)
            else:
                thumbnail_url = None
                thumbnail_path = None

            video_info = {
                "title": entry.get("title"),
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                "thumbnail_url": thumbnail_url,
                "thumbnail_path": thumbnail_path,
                "id": entry.get("id"),
                "upload_date": entry.get("upload_date"),
                "date_added": datetime.now().isoformat()
            }
            videos_data.append(video_info)
    
    return videos_data

def download_thumbnail(url, path):
    """Downloads a thumbnail image from a URL and saves it to a specified path."""
    if os.path.exists(path):
        print(f"Thumbnail already exists at {path}, skipping download.")
        return
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        print(f"Thumbnail saved to {path}")
    except Exception as e:
        print(f"Failed to download thumbnail from {url}: {e}")

def load_existing_data(filepath):
    """Loads existing video data from JSON if available."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_updated_data(filepath, data):
    """Saves updated video data to JSON."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def update_playlist_data():
    """Updates JSON with new videos from the playlist."""
    existing_data = load_existing_data(output_file)
    existing_ids = {video["id"] for video in existing_data}
    
    current_videos = fetch_playlist_videos(playlist_url)
    new_videos = [video for video in current_videos if video["id"] not in existing_ids]
    
    if new_videos:
        print(f"Found {len(new_videos)} new videos.")
        updated_data = existing_data + new_videos
        save_updated_data(output_file, updated_data)
        print("Playlist data updated.")
    else:
        print("No new videos found.")

# Run the update function
update_playlist_data()
