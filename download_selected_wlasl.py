import json
import os
import yt_dlp

# ===========================================================
# EDIT THIS LIST: which glosses (words) do you want?
# ===========================================================
TARGET_GLOSSES = ["HELLO", "PLEASE", "THANK YOU"]

# ===========================================================
# Path to WLASL JSON file
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
# Download loop
# ===========================================================
for entry in data:
    gloss = entry["gloss"].upper()

    if gloss not in [g.upper() for g in TARGET_GLOSSES]:
        continue  # skip everything except chosen words

    # --------------------------
    # Create folder for this word
    # --------------------------
    word_dir = os.path.join(OUTPUT_DIR, gloss)
    os.makedirs(word_dir, exist_ok=True)

    print(f"\n==============================")
    print(f"  DOWNLOADING WORD: {gloss}")
    print(f"  Saving to: {word_dir}")
    print(f"==============================")

    # Custom yt-dlp output path — save inside the word folder
    ydl_opts = {
        "format": "best",
        "quiet": False,
        "ignoreerrors": True,
        "outtmpl": f"{word_dir}/%(id)s.%(ext)s"
    }

    downloader = yt_dlp.YoutubeDL(ydl_opts)

    # --------------------------
    # Download each instance URL
    # --------------------------
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
