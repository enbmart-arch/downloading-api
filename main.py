from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time

app = FastAPI(title="SSS Mimic API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    target_api = "https://api-wh.sssinstagram.com/api/convert"
    
    # Current timestamp generate karna (milliseconds mein)
    current_ts = str(int(time.time() * 1000))
    
    # Ye headers website ko 'mimic' karne ke liye zaroori hain
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://sssinstagram.com",
        "Referer": "https://sssinstagram.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Payload jo aapne diya hay (Signature aur timestamps ke sath)
    # Note: Agar ye _s static nahi hay toh humein isay har bar change karna paray ga
    payload = {
        "sf_url": request.url,
        "ts": "1772560134165", # Jo aapne diya
        "_ts": "1770970183770", # Jo aapne diya
        "_tsc": "0",
        "_sv": "2",
        "_s": "4b67e2bcaa41a5f41b3a39ab416d0169c8e6f185e3653a3a4a1a0564d4d2e3d1" # Signature
    }

    try:
        response = requests.post(target_api, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "message": f"Website ne error diya: {response.status_code}",
                "raw_response": response.text
            }

        data = response.json()
        
        # Unke response se links extract karna
        # SSSInstagram aksar 'data' ya 'result' ke andar list deta hay
        media_list = []
        
        # Note: Aapko unka response check karna hoga ke wo 'data' mein hay ya 'result' mein
        # Main generic parsing likh raha hon
        items = data.get('data', []) if isinstance(data.get('data'), list) else [data.get('data')]
        
        for item in items:
            if item and isinstance(item, dict):
                url = item.get('url') or item.get('download_url')
                if url:
                    media_list.append({
                        "type": "video" if ".mp4" in url else "image",
                        "url": url,
                        "thumbnail": item.get('thumbnail') or url
                    })

        if not media_list:
            return {
                "success": False, 
                "message": "Signature invalid ho gaya hay ya URL sahi nahi hay.",
                "debug_info": data # Taake aap dekh saken unhon ne kya bheja
            }

        return {
            "success": True,
            "media": media_list,
            "original_url": request.url
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def home():
    return {"message": "SSSInstagram Mimic API is Running!"}
