from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# Aapka Google Script URL wapis add kar diya hay
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby0fPeywWQQiuJ8KG6wLEiKFGex00yjutCtJEWe6MbyU2LvXWNeHl4pw-_QKCosOaFGzQ/exec"

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    try:
        # Google ki IP use kar ke request bhejna
        response = requests.post(GOOGLE_SCRIPT_URL, json={"url": request.url}, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": "Google Bridge failed!", "details": str(e)}

@app.get("/")
def home():
    return {"message": "Dhamaka Version 9.0 - Google Bridge is BACK!"}
