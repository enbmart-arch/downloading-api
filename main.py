from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# Aapka wahi purana URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby0fPeywWQQiuJ8KG6wLEiKFGex00yjutCtJEWe6MbyU2LvXWNeHl4pw-_QKCosOaFGzQ/exec"

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    try:
        # allow_redirects=True lazmi hay kyunke Google Script redirect karta hay
        response = requests.post(GOOGLE_SCRIPT_URL, json={"url": request.url}, timeout=30, allow_redirects=True)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "message": f"Google Script ne error diya: {response.status_code}",
                "debug": response.text[:200]
            }
            
        return response.json()
    except Exception as e:
        return {"success": False, "error": "Google Bridge failed!", "details": str(e)}

@app.get("/")
def home():
    return {"message": "Google Bridge Version 2.0 is Live!"}
