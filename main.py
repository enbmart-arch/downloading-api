from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Naya aur stable bridge (igram.world logic)
    target_api = "https://api.igram.world/api/ig/posts"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Origin": "https://igram.world",
        "Referer": "https://igram.world/"
    }
    
    try:
        # Link ko clean krain
        clean_url = request.url.split('?')[0]
        
        # Request bhejna
        response = requests.post(target_api, json={"url": clean_url}, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return {"success": False, "message": "Bridge connection failed. Trying to bypass..."}

        data = response.json()
        media_list = []

        # Igram ka response format parse karna
        # Ye carousel (multiple images) ko array mein deta hay
        medias = data.get("medias", [])
        if not medias and "result" in data: # Backup check
            medias = data.get("result", [])

        for item in medias:
            url = item.get("url") or item.get("downloadUrl")
            if url:
                media_list.append({
                    "type": "video" if item.get("type") == "video" else "image",
                    "url": url,
                    "thumbnail": item.get("thumbnail") or url
                })

        if not media_list:
            return {"success": False, "message": "No media found in this post."}

        return {
            "success": True,
            "version": "6.0_STABLE_BRIDGE",
            "count": len(media_list),
            "media": media_list
        }
        
    except Exception as e:
        return {"success": False, "error": "Server error, please try again!", "details": str(e)}

@app.get("/")
def home():
    return {"message": "Dhamaka Version 6.0 - STABLE BRIDGE LIVE!"}
