from ytmusicapi import YTMusic
import svgwrite
import requests
import base64
import json
import os

# --- CONFIGURATION ---
THEME = {
    "gradient_start": "#0f0c29",
    "gradient_end": "#302b63",
    "text_color": "#ffffff",
    "artist_color": "#b3b3b3",
    "bar_color": "#F7C03C",
}

# --------------------------------------------------
# ✅ HEADERS AUTH (NOT OAUTH)
# --------------------------------------------------

HEADERS_ENV = os.getenv("YT_HEADERS_AUTH")

if not HEADERS_ENV:
    print("❌ Error: YT_HEADERS_AUTH env variable missing")
    exit(1)

try:
    headers = json.loads(HEADERS_ENV)
except json.JSONDecodeError:
    print("❌ Error: YT_HEADERS_AUTH is not valid JSON")
    exit(1)

# Initialize YTMusic using HEADERS (this is the fix)
try:
    ytmusic = YTMusic(auth=headers)
except Exception as e:
    print(f"Login Failed: {e}")
    exit(1)

# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def image_to_base64(url):
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
    except Exception:
        pass
    return None

def truncate_text(text, max_len):
    return text if len(text) <= max_len else text[:max_len-3] + "..."

# --------------------------------------------------
# SVG Generator
# --------------------------------------------------

def generate_svg():
    print("Fetching history...")
    try:
        history = ytmusic.get_history()
        if not history:
            print("No history found.")
            return
        last_watched = history[0]
    except Exception as e:
        print(f"Error fetching history: {e}")
        return

    title = last_watched.get("title", "Unknown")
    artists = (
        last_watched["artists"][0]["name"]
        if isinstance(last_watched.get("artists"), list)
        else "Unknown"
    )

    thumbnail_url = last_watched["thumbnails"][-1]["url"]
    base64_image = image_to_base64(thumbnail_url)

    width, height = 450, 140
    dwg = svgwrite.Drawing("now-playing.svg", size=(f"{width}px", f"{height}px"))

    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=12, ry=12, fill="#030303"))

    img_size, img_margin = 100, 20
    text_x = 140

    if base64_image:
        dwg.add(
            dwg.image(
                f"data:image/png;base64,{base64_image}",
                insert=(img_margin, img_margin),
                size=(img_size, img_size),
            )
        )

    dwg.add(dwg.text(truncate_text(title, 35), insert=(text_x, 50), fill="#FFFFFF", font_size=18))
    dwg.add(dwg.text(truncate_text(artists, 40), insert=(text_x, 75), fill="#AAAAAA", font_size=14))

    dwg.save()
    print("✅ Custom SVG Generated")

# --------------------------------------------------

if __name__ == "__main__":
    generate_svg()
