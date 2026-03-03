from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="Media Downloader API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            media_list = []
            
            # Agar post mein multiple images/videos hain (jaise Instagram carousel)
            if 'entries' in info:
                for entry in info['entries']:
                    # Type check karna: mp4/webm hai toh video, warna image
                    media_type = "video" if entry.get('ext') in ['mp4', 'webm'] else "image"
                    media_list.append({
                        "type": media_type,
                        "url": entry.get('url'),
                        "thumbnail": entry.get('thumbnail')
                    })
            else:
                # Agar single image ya single video hai
                media_type = "video" if info.get('ext') in ['mp4', 'webm'] else "image"
                media_list.append({
                    "type": media_type,
                    "url": info.get('url'),
                    "thumbnail": info.get('thumbnail')
                })
                
            return {
                "success": True,
                "title": info.get('title', 'Unknown'),
                "media": media_list,  # Ab yahan poori list aayegi
                "original_url": request.url
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "API ab Images aur Videos dono ke liye tayyar hay!"}
