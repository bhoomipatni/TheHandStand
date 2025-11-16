import json
import os
import yt_dlp
from pathlib import Path

# ===========================================================
# EDIT THIS LIST: which glosses (words) you want to download
# ===========================================================
TARGET_GLOSSES = ["HELLO", "PLEASE", "THANK YOU", "YES", "NO"]

# ===========================================================
# Path to JSON (place WLASL_v0.3.json in same folder as this script)
# ===========================================================
SCRIPT_DIR = Path(__file__).parent
JSON_PATH = SCRIPT_DIR / "WLASL_v0.3.json"

# ===========================================================
# Output to data/raw/wlasl (one level up from videos folder)
# ===========================================================
OUTPUT_DIR = SCRIPT_DIR / "data" / "raw" / "wlasl"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# Load dataset
# ===========================================================
if not JSON_PATH.exists():
    print(f"ERROR: {JSON_PATH} not found!")
    print("Please download WLASL_v0.3.json from https://github.com/dxli94/WLASL")
    exit(1)

print(f"Loading dataset JSON: {JSON_PATH}")
with open(JSON_PATH, "r") as f:
    data = json.load(f)

# ===========================================================
# Download loop
# ===========================================================
total_downloaded = 0
failed_downloads = []

for entry in data:
    gloss = entry["gloss"].upper()

    if gloss not in [g.upper() for g in TARGET_GLOSSES]:
        continue

    # Create folder for this specific word (lowercase for consistency)
    word_folder = OUTPUT_DIR / gloss.lower().replace(" ", "_")
    word_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"   WORD: {gloss}")
    print(f"   Target: {len(entry['instances'])} videos")
    print(f"   Saving to: {word_folder}")
    print(f"{'='*60}")

    # Set yt-dlp options
    ydl_opts = {
        "format": "best[height<=480]",  # Download lower quality for faster processing
        "quiet": False,
        "no_warnings": False,
        "ignoreerrors": True,
        "outtmpl": str(word_folder / "%(id)s.%(ext)s"),
        "postprocessors": [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert all to mp4
        }],
    }

    downloader = yt_dlp.YoutubeDL(ydl_opts)

    downloaded_count = 0
    # Loop through all instances for this gloss
    for inst in entry["instances"]:
        url = inst.get("url")
        vid = inst.get("video_id")

        if not url:
            print(f"  ⊗ Skipping {vid}: No URL available.")
            continue

        # Check if already downloaded
        existing_files = list(word_folder.glob(f"{vid}.*"))
        if existing_files:
            print(f"  ✓ Already downloaded: {vid}")
            downloaded_count += 1
            continue

        print(f"  → Downloading video_id {vid}...", end=" ")

        try:
            downloader.download([url])
            downloaded_count += 1
            total_downloaded += 1
            print("✓")
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed_downloads.append({
                'word': gloss,
                'video_id': vid,
                'url': url,
                'error': str(e)
            })

    print(f"  Downloaded {downloaded_count}/{len(entry['instances'])} videos for '{gloss}'")

# ===========================================================
# Summary
# ===========================================================
print(f"\n{'='*60}")
print(f"DOWNLOAD COMPLETE!")
print(f"{'='*60}")
print(f"Total videos downloaded: {total_downloaded}")
print(f"Failed downloads: {len(failed_downloads)}")
print(f"Output location: {OUTPUT_DIR}")

if failed_downloads:
    print(f"\nFailed downloads:")
    for fail in failed_downloads[:10]:  # Show first 10
        print(f"  - {fail['word']}: {fail['video_id']}")
    
    # Save failed downloads to JSON
    failed_path = SCRIPT_DIR / "failed_downloads.json"
    with open(failed_path, 'w') as f:
        json.dump(failed_downloads, f, indent=2)
    print(f"\nFull list saved to: {failed_path}")

print(f"\n{'='*60}")
print("NEXT STEPS:")
print("1. Run: python src/data/extract_keypoints.py")
print("2. Then: python src/models/train.py")
print(f"{'='*60}")
