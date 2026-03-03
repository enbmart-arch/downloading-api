from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time

app = FastAPI(title="SSS Mimic API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Website ka asli backend endpoint
    target_api = "https://api-wh.sssinstagram.com/api/convert"
    
    # Headers jo website ko mimic krain ge
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://sssinstagram.com",
        "Referer": "https://sssinstagram.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Payload jo aap ne provide kiya tha
    # NOTE: Agar ye _s static nahi hay, toh ye method fail ho sakta hay
    payload = {
        "sf_url": request.url,
        "ts": "1772560134165",
        "_ts": "1770970183770",
        "_tsc": "0",
        "_sv": "2",
        "_s": "4b67e2bcaa41a5f41b3a39ab416d0169c8e6f185e3653a3a4a1a0564d4d2e3d1"
    }

    try:
        # Request bhejna
        response = requests.post(target_api, json=payload, headers=headers, timeout=20)
        
        # Check krain ke website ne kya jawab diya
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Website ne error diya code: {response.status_code}",
                "raw_body": response.text[:500] # Pehle 500 characters check karne ke liye
            }

        data = response.json()
        
        # Agar response mein data mil jaye
        if "data" in data:
            return {
                "success": True,
                "data": data["data"], # SSS ka asli response
                "original_url": request.url
            }
        else:
            return {
                "success": False,
                "message": "Signature expired ya invalid link!",
                "full_response": data
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def home():
    return {"message": "Mimic API is Live. Testing SSS Endpoint..."}
