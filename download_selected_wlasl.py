import json
import os
import yt_dlp

# ===========================================================
# EDIT THIS LIST: which glosses (words) do you want?
# Example: ["HELLO", "PLEASE", "THANK YOU"]
# ===========================================================
TARGET_GLOSSES = ["HELLO", "PLEASE", "THANK YOU"]


# ===========================================================
# Path to WLASL JSON file
# Make sure you put the JSON inside your project folder
# ===========================================================
JSON_PATH = "WLASL_v0.3.json"

# ===========================================================
# Output folder where videos will be saved
# ===========================================================
OUTPUT_DIR = "selected_wlasl_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================================================
# Load dataset JSON
# ===========================================================
print(f"Loading dataset JSON: {JSON_PATH}")
with open(JSON_PATH, "r") as f:
    data = json.load(f)

# ===========================================================
# yt-dlp setup
# ===========================================================
ydl_opts = {
    "format": "best",
    "quiet": False,
    "ignoreerrors": True,
    "outtmpl": f"{OUTPUT_DIR}/%(id)s.%(ext)s"
}

downloader = yt_dlp.YoutubeDL(ydl_opts)

# ===========================================================
# Download loop
# ===========================================================
for entry in data:
    gloss = entry["gloss"].upper()

    if gloss not in [g.upper() for g in TARGET_GLOSSES]:
        continue  # skip everything except chosen words

    print(f"\n==============================")
    print(f"  DOWNLOADING WORD: {gloss}")
    print(f"==============================")

    for inst in entry["instances"]:
        url = inst.get("url")
        vid = inst.get("video_id")

        if not url:
            print(f"Skipping {vid}: No URL available")
            continue

        print(f"→ Downloading video_id {vid}")

        try:
            downloader.download([url])
        except Exception as e:
            print(f"FAILED for {vid}: {e}")

print("\nDONE! Your selected videos are in:", OUTPUT_DIR)
