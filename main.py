from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# Aapka Google Apps Script URL yahan set kar diya hay
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby0fPeywWQQiuJ8KG6wLEiKFGex00yjutCtJEWe6MbyU2LvXWNeHl4pw-_QKCosOaFGzQ/exec"

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    try:
        # Render ab direct Instagram ko hit nahi karega, balkay Google Script ko request bhejay ga
        response = requests.post(GOOGLE_SCRIPT_URL, json={"url": request.url}, timeout=30)
        
        if response.status_code != 200:
            return {"success": False, "message": "Google Script ne respond nahi kiya."}
            
        return response.json()
    except Exception as e:
        return {"success": False, "error": "Google Bridge failed!", "details": str(e)}

@app.get("/")
def home():
    return {"message": "Google Proxy Bridge is Live and Ready!"}
