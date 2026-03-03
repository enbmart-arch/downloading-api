from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="Ultimate Downloader API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # In settings se yt-dlp deep search karega har image ke liye
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'extract_flat': False, # Ye zaroori hay carousel ki sari images ke liye
        'force_generic_extractor': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # URL ko clean karna (extra parameters hatana)
            clean_url = request.url.split('?')[0]
            info = ydl.extract_info(clean_url, download=False)
            
            media_list = []
            
            # Agar entries majood hain (Carousel/Playlist)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        # Har entry ka best quality link nikalna
                        url = entry.get('url') or entry.get('thumbnail')
                        ext = entry.get('ext', '')
                        m_type = "video" if ext in ['mp4', 'webm'] or (url and '.mp4' in url) else "image"
                        
                        media_list.append({
                            "type": m_type,
                            "url": url,
                            "thumbnail": entry.get('thumbnail')
                        })
            
            # Agar single post hay
            else:
                url = info.get('url') or info.get('thumbnail')
                ext = info.get('ext', '')
                m_type = "video" if ext in ['mp4', 'webm'] or (url and '.mp4' in url) else "image"
                
                media_list.append({
                    "type": m_type,
                    "url": url,
                    "thumbnail": info.get('thumbnail')
                })

            return {
                "success": True,
                "title": info.get('title', 'Instagram Post'),
                "media_count": len(media_list),
                "media": media_list,
                "original_url": request.url
            }

    except Exception as e:
        # Agar block ho jaye toh error message show kare
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "API is online! Trying to bypass restrictions..."}
