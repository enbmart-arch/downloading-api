from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Ye target API carousels aur reels dono handle karti hay
    target_api = "https://api.vveet.com/v1/ig/info"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://vveet.com",
        "Referer": "https://vveet.com/"
    }
    
    try:
        # URL se extra kachra saaf karna
        clean_url = request.url.split('?')[0]
        
        # Request bhejna
        response = requests.post(target_api, json={"url": clean_url}, headers=headers, timeout=15)
        data = response.json()
        
        media_list = []
        # JSON se images aur videos nikalna
        if "data" in data and "medias" in data["data"]:
            for item in data["data"]["medias"]:
                media_list.append({
                    "type": "video" if item.get("type") == "video" else "image",
                    "url": item.get("url"),
                    "thumbnail": item.get("thumbnail") or item.get("url")
                })

        if not media_list:
            return {"success": False, "message": "Scraper ne koi data nahi diya. Link check krain."}

        return {
            "success": True,
            "version": "5.0_FINAL_NO_YT_DLP",
            "title": data.get("data", {}).get("title", "Instagram Post"),
            "count": len(media_list),
            "media": media_list
        }
        
    except Exception as e:
        return {"success": False, "error": "Server busy ya link invalid hay!", "details": str(e)}

@app.get("/")
def home():
    # Is message se confirm hoga ke naya code chal raha hay
    return {"message": "Dhamaka Version 5.0 - NO YT-DLP LIVE!"}
