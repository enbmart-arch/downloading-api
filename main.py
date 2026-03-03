from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import re

app = FastAPI(title="Media Bridge API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Target: Aik aisi site jo carousel handle karti hay
    target_api = "https://api.vveet.com/v1/ig/info"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
        "Origin": "https://vveet.com",
        "Referer": "https://vveet.com/"
    }
    
    # URL ko clean krain
    clean_url = request.url.split('?')[0]
    payload = {"url": clean_url}

    try:
        # Request bhejna
        response = requests.post(target_api, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {"success": False, "message": "Third-party scraper block ho gaya hay."}

        data = response.json()
        media_list = []

        # JSON response ko parhna (Parsing)
        if "data" in data and "medias" in data["data"]:
            for item in data["data"]["medias"]:
                media_list.append({
                    "type": "video" if item.get("type") == "video" else "image",
                    "url": item.get("url"),
                    "thumbnail": item.get("thumbnail") or item.get("url")
                })

        if not media_list:
            return {"success": False, "message": "Koi media nahi mila. Link check krain."}

        return {
            "success": True,
            "title": data.get("data", {}).get("title", "Instagram Post"),
            "count": len(media_list),
            "media": media_list
        }

    except Exception as e:
        return {"success": False, "error": "Server Busy! Dobara koshish krain."}

@app.get("/")
def home():
    return {"message": "Bridge API is active. No yt-dlp here!"}
