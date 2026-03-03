from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="Media Downloader API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            media_list = []
            
            # Agar multiple posts (carousel) hain aur list khali nahi hay
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if entry is None: # Agar koi item fetch na ho sakay toh skip krain
                        continue
                        
                    ext = entry.get('ext', '')
                    media_type = "video" if ext in ['mp4', 'webm'] else "image"
                    
                    # Images ke case mein kabhi direct 'url' nahi milta, wahan hum thumbnail use krain ge
                    media_url = entry.get('url')
                    if not media_url:
                        media_url = entry.get('thumbnail')
                        
                    if media_url: 
                        media_list.append({
                            "type": media_type,
                            "url": media_url,
                            "thumbnail": entry.get('thumbnail')
                        })
            else:
                # Agar single image/video hay
                ext = info.get('ext', '')
                media_type = "video" if ext in ['mp4', 'webm'] else "image"
                
                media_url = info.get('url')
                if not media_url:
                    media_url = info.get('thumbnail')
                    
                if media_url:
                    media_list.append({
                        "type": media_type,
                        "url": media_url,
                        "thumbnail": info.get('thumbnail')
                    })
            
            # Agar aakhir mein koi bhi link na milay
            if len(media_list) == 0:
                raise Exception("Media nahi mila. Shayad account private hay ya link invalid hay.")
                
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
    return {"message": "API is working perfectly for both Images and Videos!"}
