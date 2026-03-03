from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="Video Downloader API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_video_info(request: VideoRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return {
                "success": True,
                "title": info.get('title', 'Unknown'),
                "download_url": info.get('url', None),
                "thumbnail": info.get('thumbnail', None)
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "Aapki API chal rahi hay!"}
