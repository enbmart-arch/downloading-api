from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Hum aik naya stable scraper use kar rahay hain (SnapInsta type logic)
    target_api = "https://api.vveet.com/v1/ig/info"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        # Clean URL
        clean_url = request.url.split('?')[0]
        response = requests.post(target_api, json={"url": clean_url}, headers=headers, timeout=15)
        data = response.json()
        
        media_list = []
        if "data" in data and "medias" in data["data"]:
            for item in data["data"]["medias"]:
                media_list.append({
                    "type": "video" if item.get("type") == "video" else "image",
                    "url": item.get("url"),
                    "thumbnail": item.get("thumbnail") or item.get("url")
                })

        if not media_list:
            return {"success": False, "message": "Scraper ne data nahi diya."}

        return {
            "success": True,
            "version": "5.0_NO_YT_DLP", # Is line se humein pata chalay ga naya code hay
            "media": media_list
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def home():
    # Is message ko browser mein check krain
    return {"message": "Dhamaka Version 5.0 - NO YT-DLP LIVE!"}
