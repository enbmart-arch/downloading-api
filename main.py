from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI(title="Pro Media Downloader API")

class VideoRequest(BaseModel):
    url: str

def get_media_item(item):
    url = item.get('url')
    ext = item.get('ext', '')
    if not url:
        thumbnails = item.get('thumbnails', [])
        if thumbnails:
            url = thumbnails[-1].get('url') # High quality image
        else:
            url = item.get('thumbnail')
            
    if not url: return None
        
    media_type = "video" if ext in ['mp4', 'webm'] or '.mp4' in url else "image"
    return {"type": media_type, "url": url, "thumbnail": item.get('thumbnail') or url}

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Check krain ke cookies file majood hay ya nahi
    cookie_path = 'cookies.txt'
    has_cookies = os.path.exists(cookie_path)
    
    ydl_opts = {
        'quiet': True, 
        'skip_download': True, 
        'no_warnings': True, 
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    # Agar cookies file upload ki gayi hay, toh usay use krain
    if has_cookies:
        ydl_opts['cookiefile'] = cookie_path
    
    media_list = []
    title = "Instagram Media"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            title = info.get('title', 'Instagram Post')
            
            # Carousel (Multiple Images/Videos) handle karna
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry:
                        m_item = get_media_item(entry)
                        if m_item: media_list.append(m_item)
            # Single Image/Video handle karna
            else:
                m_item = get_media_item(info)
                if m_item: media_list.append(m_item)
                
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "original_url": request.url}

    if not media_list:
        return {"success": False, "message": "Media nahi mila. Agar ye carousel hay toh cookies.txt lazmi upload krain.", "original_url": request.url}
        
    return {"success": True, "title": title, "media": media_list, "original_url": request.url}

@app.get("/")
def home():
    return {"message": "Pro API with Cookies Support is Running!"}
