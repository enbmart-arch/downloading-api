from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import urllib.request
import json
import re

app = FastAPI(title="Media Downloader API")

class VideoRequest(BaseModel):
    url: str

def get_media_item(item):
    url = item.get('url')
    ext = item.get('ext', '')
    if not url:
        thumbnails = item.get('thumbnails', [])
        if thumbnails:
            url = thumbnails[-1].get('url')
        else:
            url = item.get('thumbnail')
            
    if not url: return None
        
    media_type = "video" if ext in ['mp4', 'webm'] or '.mp4' in url else "image"
    return {"type": media_type, "url": url, "thumbnail": item.get('thumbnail') or url}

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    ydl_opts = {
        'quiet': True, 'skip_download': True, 'no_warnings': True, 'extract_flat': False,
        # Agar aap cookies add karein toh ye line uncomment kar dijiyega:
        # 'cookiefile': 'cookies.txt', 
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    }
    
    media_list = []
    title = "Instagram Media"
    
    # Engine 1: yt-dlp (Videos ke liye)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            title = info.get('title', 'Instagram Post')
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry:
                        m_item = get_media_item(entry)
                        if m_item: media_list.append(m_item)
            else:
                m_item = get_media_item(info)
                if m_item: media_list.append(m_item)
    except Exception:
        pass

    # Engine 2: Alternative Cobalt Instance (co.wuk.sh - Carousels ke liye)
    if not media_list and "instagram.com" in request.url:
        try:
            req = urllib.request.Request(
                "https://co.wuk.sh/api/json",
                data=json.dumps({"url": request.url, "vQuality": "max"}).encode('utf-8'),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
            )
            res = urllib.request.urlopen(req).read()
            data = json.loads(res.decode('utf-8'))
            
            if data.get('status') == 'picker':
                for item in data.get('picker', []):
                    media_list.append({
                        "type": "video" if item.get('type') == 'video' else "image",
                        "url": item.get('url'),
                        "thumbnail": item.get('thumb') or item.get('url')
                    })
            elif data.get('status') in ['redirect', 'success', 'stream']:
                url = data.get('url')
                if url:
                    media_list.append({"type": "video" if ".mp4" in url else "image", "url": url, "thumbnail": url})
        except Exception:
            pass

    # Engine 3: Embed Fallback (Akhri Rasta)
    if not media_list and "instagram.com" in request.url:
        try:
            shortcode_match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', request.url)
            if shortcode_match:
                shortcode = shortcode_match.group(1)
                embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
                req = urllib.request.Request(embed_url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read().decode('utf-8')
                img_match = re.search(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', html)
                if not img_match:
                    img_match = re.search(r'src="([^"]+\.jpg[^"]*)"', html)
                if img_match:
                    img_url = img_match.group(1).replace("&amp;", "&")
                    media_list.append({"type": "image", "url": img_url, "thumbnail": img_url})
        except Exception:
            pass

    if not media_list:
        return {"success": False, "message": "API blocked. Cookies setup required.", "original_url": request.url}
        
    return {"success": True, "title": title, "media": media_list, "original_url": request.url}

@app.get("/")
def home():
    return {"message": "API with Alternative Proxy Engine Running!"}
