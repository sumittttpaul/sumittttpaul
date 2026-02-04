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
    if "YT_HEADERS_AUTH" in os.environ:
        with open("oauth.json", "w") as f:
            f.write(os.environ["YT_HEADERS_AUTH"])
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

    # --- 1. Extract Data ---
    title = last_watched['title']
    # Handle artist list safely
    if isinstance(last_watched.get("artists"), list):
        artists = last_watched['artists'][0]['name']
    else:
        artists = (last_watched.get("artists") or "Unknown")

    thumbnail_url = last_watched['thumbnails'][-1]['url'] # Get largest image
    base64_image = image_to_base64(thumbnail_url)

    # --- 2. Canvas Setup (YouTube Music Dark Theme) ---
    width = 450
    height = 140
    dwg = svgwrite.Drawing("now-playing.svg", profile='full', size=(f"{width}px", f"{height}px"))

    # Define Fonts
    dwg.defs.add(dwg.style("""
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        .title { font-family: 'Roboto', sans-serif; font-size: 18px; font-weight: 700; fill: #FFFFFF; }
        .artist { font-family: 'Roboto', sans-serif; font-size: 14px; font-weight: 400; fill: #AAAAAA; }
        .bar-bg { fill: #333333; rx: 2px; }
        .bar-fill { fill: #FFFFFF; rx: 2px; }
        .icon { fill: #FFFFFF; }
        
        /* Animations */
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.02); opacity: 0.9; }
            100% { transform: scale(1); opacity: 1; }
        }
        .artwork { animation: pulse 4s infinite ease-in-out; transform-origin: center; }
    """))

    # Background (Dark Grey)
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=12, ry=12, fill="#030303"))

    # --- 3. Artwork (Left) ---
    img_size = 100
    img_margin = 20
    
    # Clip Path for Rounded Image
    clip_id = "img_clip"
    clip = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip.add(dwg.rect(insert=(img_margin, img_margin), size=(img_size, img_size), rx=8, ry=8))

    if base64_image:
        # Shadow
        dwg.add(dwg.rect(insert=(img_margin+4, img_margin+4), size=(img_size, img_size), rx=8, ry=8, fill="#000000", fill_opacity=0.5))
        # Image with class for animation
        img = dwg.image(f"data:image/png;base64,{base64_image}", insert=(img_margin, img_margin), size=(img_size, img_size), clip_path=f"url(#{clip_id})")
        img['class'] = 'artwork'
        dwg.add(img)

    # --- 4. Text & UI (Right) ---
    text_x = 140
    
    # Title (Truncate if needed manually, or let SVG handle it)
    display_title = title if len(title) < 35 else title[:32] + "..."
    dwg.add(dwg.text(display_title, insert=(text_x, 50), class_="title"))
    
    # Artist
    display_artist = artists if len(artists) < 40 else artists[:37] + "..."
    dwg.add(dwg.text(display_artist, insert=(text_x, 75), class_="artist"))

    # --- 5. Player Controls & Bar ---
    # Progress Bar Background
    bar_y = 105
    dwg.add(dwg.rect(insert=(text_x, bar_y), size=(260, 4), class_="bar-bg"))
    
    # Progress Bar Fill (Fixed at 60% for aesthetics)
    dwg.add(dwg.rect(insert=(text_x, bar_y), size=(160, 4), class_="bar-fill"))
    
    # Current Time / Total Time (Fake values for look)
    dwg.add(dwg.text("2:14", insert=(text_x, bar_y + 18), font_size="10px", font_family="Roboto", fill="#AAAAAA"))
    dwg.add(dwg.text("3:45", insert=(width - 50, bar_y + 18), font_size="10px", font_family="Roboto", fill="#AAAAAA", text_anchor="end"))

    # Logo (YTM Logo placeholder - simple circle/triangle)
    logo_x = width - 40
    logo_y = 20
    dwg.add(dwg.circle(center=(logo_x, logo_y), r=12, fill="#FF0000"))
    dwg.add(dwg.polygon(points=f"{logo_x-3},{logo_y-5} {logo_x-3},{logo_y+5} {logo_x+5},{logo_y}", fill="white"))

    dwg.save()
    print("Custom SVG Generated.")

if __name__ == "__main__":
    generate_svg()
