from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI(title="Media Bridge API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    try:
        # Step 1: Target API (Inshallah ye block nahi hogi)
        # Ye aik reliable third-party processor hay
        api_url = "https://api.vveet.com/v1/ig/info"
        
        # Instagram link ko clean krain
        clean_url = request.url.split('?')[0]
        
        payload = {"url": clean_url}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"
        }

        # Request bhejna
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise Exception("Third-party server ne respond nahi kiya.")

        data = response.json()
        media_list = []

        # Step 2: Response check krain (Agar carousel hay)
        if "data" in data and "medias" in data["data"]:
            for item in data["data"]["medias"]:
                media_list.append({
                    "type": "video" if item.get("type") == "video" else "image",
                    "url": item.get("url"),
                    "thumbnail": item.get("thumbnail") or item.get("url")
                })
        
        if not media_list:
            return {"success": False, "message": "Media links nahi mil sakay."}

        return {
            "success": True,
            "title": data.get("data", {}).get("title", "Instagram Post"),
            "count": len(media_list),
            "media": media_list
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Scraper method mein masla aaya hay.",
            "error": str(e)
        }

@app.get("/")
def home():
    return {"message": "Bridge API is active and ready to scrape!"}
