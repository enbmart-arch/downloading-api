from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="Media Downloader API")

class VideoRequest(BaseModel):
    url: str

# Ek naya function jo list mein se sahi link dhoondega
def get_media_item(item):
    url = item.get('url')
    ext = item.get('ext', '')
    
    # Agar direct URL na milay (yani ye image hay), toh thumbnails mein se high-quality link nikal lo
    if not url:
        thumbnails = item.get('thumbnails', [])
        if thumbnails:
            url = thumbnails[-1].get('url') # [-1] ka matlab sab se aakhri (sab se bari) resolution
        else:
            url = item.get('thumbnail')
            
    if not url:
        return None
        
    # Check krain ke url mp4 hay ya image
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
        'extract_flat': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            media_list = []
            
            # Agar post mein ek se zyada items hain (Carousel)
            if 'entries
