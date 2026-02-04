import os
import base64
import requests
import svgwrite
from ytmusicapi import YTMusic

# --- CONFIGURATION ---
THEME = {
    "gradient_start": "#0f0c29",
    "gradient_end": "#302b63",
    "text_color": "#ffffff",
    "artist_color": "#b3b3b3",
    "bar_color": "#F7C03C",
}

# Setup Auth
if not os.path.exists("oauth.json"):
    # FIX: Changed "YT_HEADERS_AUTH" to "HEADERS_AUTH" to match your Workflow file
    if "HEADERS_AUTH" in os.environ:
        with open("oauth.json", "w") as f:
            f.write(os.environ["HEADERS_AUTH"])
    else:
        print("Error: No oauth.json found. Check your YAML 'env' section.")
        exit(1)

# Initialize API
try:
    ytmusic = YTMusic("oauth.json")
except Exception as e:
    print(f"Login Failed: {e}")
    exit(1)

def image_to_base64(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
    except:
        pass
    return None

def truncate_text(text, max_len):
    return text if len(text) <= max_len else text[:max_len-3] + "..."

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

    # Extract Data
    title = truncate_text(last_watched['title'], 25)
    artists = truncate_text((last_watched.get("artists") or [{"name": "Unknown"}])[0]['name'], 30)
    thumbnail_url = last_watched['thumbnails'][0]['url']
    base64_image = image_to_base64(thumbnail_url)

    # Canvas Settings
    width = 400
    height = 120
    dwg = svgwrite.Drawing("now-playing.svg", profile='full', size=(f"{width}px", f"{height}px"))

    # 1. Background Gradient
    grad = dwg.linearGradient(start=(0, 0), end=(1, 0), id="bg_grad")
    grad.add_stop_color(0, THEME["gradient_start"])
    grad.add_stop_color(1, THEME["gradient_end"])
    dwg.defs.add(grad)

    # Main Card Body
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=15, ry=15, fill="url(#bg_grad)"))

    # 2. Glass Overlay
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "50%"), rx=15, ry=15, fill="#ffffff", fill_opacity=0.05))

    # 3. Album Art
    img_size = 80
    img_margin = 20
    clip_id = "img_clip"
    clip = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip.add(dwg.rect(insert=(img_margin, img_margin), size=(img_size, img_size), rx=10, ry=10))

    if base64_image:
        dwg.add(dwg.rect(insert=(img_margin+4, img_margin+4), size=(img_size, img_size), rx=10, ry=10, fill="#000000", fill_opacity=0.3))
        dwg.add(dwg.image(f"data:image/png;base64,{base64_image}", insert=(img_margin, img_margin), size=(img_size, img_size), clip_path=f"url(#{clip_id})"))

    # 4. Text Info
    text_x = 120
    dwg.add(dwg.text("NOW PLAYING", insert=(text_x, 35), fill=THEME["bar_color"], font_size=10, font_family="Segoe UI, Verdana, sans-serif", font_weight="bold", letter_spacing=1))
    dwg.add(dwg.text(title, insert=(text_x, 60), fill=THEME["text_color"], font_size=18, font_family="Segoe UI, Verdana, sans-serif", font_weight="bold"))
    dwg.add(dwg.text(artists, insert=(text_x, 85), fill=THEME["artist_color"], font_size=14, font_family="Segoe UI, Verdana, sans-serif"))

    # 5. Progress Bar
    bar_y = 100
    dwg.add(dwg.rect(insert=(text_x, bar_y), size=(200, 4), rx=2, ry=2, fill="#ffffff", fill_opacity=0.2))
    dwg.add(dwg.rect(insert=(text_x, bar_y), size=(120, 4), rx=2, ry=2, fill=THEME["bar_color"]))

    dwg.save()
    print("SVG Generated successfully.")

if __name__ == "__main__":
    generate_svg()
