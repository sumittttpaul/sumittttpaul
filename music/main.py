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
    except Exception as e:
        print(f"⚠️ Auth or network error while fetching history: {e}")
        return

    if not history:
        print("ℹ️ No history found (empty response)")
        return

    last_watched = history[0]

    title = last_watched.get("title", "Unknown")
    artists = (
        last_watched["artists"][0]["name"]
        if isinstance(last_watched.get("artists"), list)
        else "Unknown"
    )

    thumbnail_url = last_watched["thumbnails"][-1]["url"]
    base64_image = image_to_base64(thumbnail_url)

    # --- SVG CONFIG ---
    width, height = 450, 140
    output_file = "now-playing.svg"

    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
        xmlns="http://www.w3.org/2000/svg">

    <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0f0f0f"/>
        <stop offset="100%" stop-color="#181818"/>
        </linearGradient>

        <clipPath id="art">
        <rect x="20" y="20" rx="10" ry="10" width="100" height="100"/>
        </clipPath>
    </defs>

    <!-- Background -->
    <rect width="100%" height="100%" rx="16" fill="url(#bg)"/>

    <!-- Album shadow -->
    <rect x="24" y="24" rx="10" ry="10" width="100" height="100"
            fill="black" opacity="0.35"/>

    <!-- Album art -->
    {"<image href='data:image/png;base64," + base64_image + "' x='20' y='20' width='100' height='100' clip-path='url(#art)'/>" if base64_image else ""}

    <!-- Title -->
    <text x="140" y="55"
            fill="#ffffff"
            font-size="17"
            font-weight="700"
            font-family="system-ui, -apple-system, Segoe UI, Roboto">
        {truncate_text(title, 35)}
    </text>

    <!-- Artist -->
    <text x="140" y="78"
            fill="#aaaaaa"
            font-size="14"
            font-family="system-ui, -apple-system, Segoe UI, Roboto">
        {truncate_text(artists, 40)}
    </text>

    <!-- Progress bar -->
    <rect x="140" y="100" width="260" height="4" rx="2" fill="#333"/>
    <rect x="140" y="100" width="160" height="4" rx="2" fill="#ff0033"/>

    <!-- YouTube Music icon -->
    <circle cx="415" cy="35" r="10" fill="#ff0033"/>
    <polygon points="412,30 412,40 420,35" fill="white"/>

    <!-- Footer -->
    <text x="140" y="125"
            fill="#666"
            font-size="10"
            font-family="system-ui">
        🎧 Now Playing on YouTube Music
    </text>

    </svg>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg)

    print("✅ SVG Generated:", output_file)


# --------------------------------------------------

if __name__ == "__main__":
    generate_svg()
