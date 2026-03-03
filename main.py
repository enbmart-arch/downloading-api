from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="Media Downloader API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Yahan humne Fake Browser Header add kiya hay taake Instagram block na kare
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            media_list = []
            
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry:
                        # Direct url check krain, na milay toh thumbnail utha lain
                        url = entry.get('url') or entry.get('thumbnail')
                        if url:
                            media_list.append({
                                "type": "video" if entry.get('ext') in ['mp4', 'webm'] else "image",
                                "url": url,
                                "thumbnail": entry.get('thumbnail')
                            })
            else:
                url = info.get('url') or info.get('thumbnail')
                if url:
                    media_list.append({
                        "type": "video" if info.get('ext') in ['mp4', 'webm'] else "image",
                        "url": url,
                        "thumbnail": info.get('thumbnail')
                    })
            
            # Agar security ki wajah se link na milay toh proper message aye
            if not media_list:
                return {
                    "success": False, 
                    "message": "Instagram ne media block kar diya hay (Private account ya login required).",
                    "original_url": request.url
                }
                
            return {
                "success": True,
                "title": info.get('title', 'Unknown'),
                "media": media_list,
                "original_url": request.url
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "API with Anti-Block Headers is running!"}
