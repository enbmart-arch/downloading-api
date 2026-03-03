from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

def try_engine_1(insta_url):
    # Engine 1: Publer (Bohat stable hay)
    try:
        api_url = "https://publer.io/api/v1/social-provider/instagram/info"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://publer.io",
            "Referer": "https://publer.io/"
        }
        response = requests.post(api_url, json={"url": insta_url}, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            media_list = []
            # Publer ka response format
            for item in data.get('media', []):
                media_list.append({
                    "type": "video" if item.get('type') == 'video' else "image",
                    "url": item.get('url'),
                    "thumbnail": item.get('thumbnail') or item.get('url')
                })
            return media_list
    except:
        return None

def try_engine_2(insta_url):
    # Engine 2: Alternative stable bridge
    try:
        api_url = "https://api.vveet.com/v1/ig/info"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.post(api_url, json={"url": insta_url}, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            media_list = []
            for item in data.get('data', {}).get('medias', []):
                media_list.append({
                    "type": item.get('type'),
                    "url": item.get('url'),
                    "thumbnail": item.get('thumbnail')
                })
            return media_list
    except:
        return None

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    clean_url = request.url.split('?')[0]
    
    # Pehle Engine 1 koshish karega
    result = try_engine_1(clean_url)
    
    # Agar fail hua toh Engine 2
    if not result:
        result = try_engine_2(clean_url)
        
    if result:
        return {
            "success": True,
            "version": "7.0_MULTI_ENGINE",
            "count": len(result),
            "media": result
        }
    
    return {
        "success": False, 
        "message": "Saray engines block ho gaye hain. Instagram security tight hay."
    }

@app.get("/")
def home():
    return {"message": "Dhamaka Version 7.0 - MULTI ENGINE LIVE!"}
