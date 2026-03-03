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
    
    # Engine 1: Videos aur normal media ke liye (yt-dlp)
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
        pass # Agar library fail ho, toh chup chap Engine 2 par jao

    # Engine 2: The "Embed Page" Bypass Trick (Khaas Images ke liye)
    if not media_list and "instagram.com" in request.url:
        try:
            # URL se sirf shortcode nikalna
            shortcode_match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', request.url)
            if shortcode_match:
                shortcode = shortcode_match.group(1)
                
                # Embed URL create karna jo Login bypass karta hay
                embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
                
                req = urllib.request.Request(
                    embed_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                html_bytes = urllib.request.urlopen(req).read()
                html = html_bytes.decode('utf-8')
                
                # Embed code ke andar se tasweer dhoondna
                img_match = re.search(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', html)
                if not img_match:
                    img_match = re.search(r'src="([^"]+\.jpg[^"]*)"', html)
                    
                if img_match:
                    image_url = img_match.group(1).replace("&amp;", "&")
                    media_list.append({
                        "type": "image",
                        "url": image_url,
                        "thumbnail": image_url
                    })
                    title = "Instagram Image"
        except Exception as backup_error:
            pass

    # Agar phir bhi dono engines fail ho jayen
    if not media_list:
        return {
            "success": False, 
            "message": "Account shayad completely private hay.",
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
    return {"message": "API with Embed-Bypass Engine is fully active!"}
