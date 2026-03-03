from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import urllib.request
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
            
    if not url:
        return None
        
    media_type = "video" if ext in ['mp4', 'webm'] or '.mp4' in url else "image"
    
    return {
        "type": media_type,
        "url": url,
        "thumbnail": item.get('thumbnail') or url
    }

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    media_list = []
    title = "Unknown"
    
    # Engine 1: yt-dlp (Videos aur supported media ke liye)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            title = info.get('title', 'Instagram Post')
            
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry:
                        media_item = get_media_item(entry)
                        if media_item:
                            media_list.append(media_item)
            else:
                media_item = get_media_item(info)
                if media_item:
                    media_list.append(media_item)
    except Exception as e:
        pass # Agar yt-dlp fail ho jaye, toh hum chup chap Engine 2 par chale jayenge

    # Engine 2: Custom HTML Scraper (Khaas tor par Instagram Images aur Carousels ke liye)
    if not media_list and "instagram.com" in request.url:
        try:
            req = urllib.request.Request(
                request.url, 
                headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
            )
            html_bytes = urllib.request.urlopen(req).read()
            html_content = html_bytes.decode('utf-8')
            
            # Webpage ke source code se direct High-Res Image ka link nikalna
            match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
            if match:
                image_url = match.group(1).replace("&amp;", "&")
                media_list.append({
                    "type": "image",
                    "url": image_url,
                    "thumbnail": image_url
                })
                title = "Instagram Image Post"
        except Exception as backup_error:
            pass

    # Agar dono engines fail ho jayen (Private account ki wajah se)
    if not media_list:
        return {
            "success": False, 
            "message": "Account private hay ya link block ho gaya hay.",
            "original_url": request.url
        }
        
    return {
        "success": True,
        "title": title,
        "media": media_list,
        "original_url": request.url
    }

@app.get("/")
def home():
    return {"message": "API with Dual Engine (Video + Image Scraper) is running!"}
