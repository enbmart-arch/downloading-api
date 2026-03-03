from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import json
import re
import urllib.request

app = FastAPI(title="Pro Downloader API")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def get_media_info(request: VideoRequest):
    # Standard yt-dlp options
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.instagram.com/',
        }
    }
    
    # Check krain ke cookies file GitHub par upload hay ya nahi
    import os
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            media_list = []
            
            # Case 1: Carousel (Multiple Items)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        url = entry.get('url') or entry.get('thumbnail')
                        ext = entry.get('ext', '')
                        m_type = "video" if ext in ['mp4', 'webm'] or (url and '.mp4' in url) else "image"
                        media_list.append({"type": m_type, "url": url, "thumbnail": entry.get('thumbnail')})
            
            # Case 2: Single Post
            else:
                url = info.get('url') or info.get('thumbnail')
                ext = info.get('ext', '')
                m_type = "video" if ext in ['mp4', 'webm'] or (url and '.mp4' in url) else "image"
                media_list.append({"type": m_type, "url": url, "thumbnail": info.get('thumbnail')})

            if media_list:
                return {
                    "success": True,
                    "title": info.get('title', 'Instagram Post'),
                    "count": len(media_list),
                    "media": media_list
                }
            
            raise Exception("Media list empty")

    except Exception:
        # Agar yt-dlp fail ho jaye toh Manual JSON Scraper (Bypass Trick)
        try:
            req = urllib.request.Request(request.url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('utf-8')
            
            # Instagram ke hidden JSON data mein se links nikalna
            links = re.findall(r'"display_url":"([^"]+)"', html)
            if links:
                # Duplicate links hatana
                unique_links = list(dict.fromkeys(links))
                final_media = []
                for l in unique_links:
                    final_media.append({"type": "image", "url": l.replace('\\u0026', '&'), "thumbnail": l.replace('\\u0026', '&')})
                
                return {
                    "success": True,
                    "title": "Instagram Carousel (Manual)",
                    "count": len(final_media),
                    "media": final_media
                }
        except:
            pass
            
        return {
            "success": False,
            "message": "Instagram security wall! Please upload cookies.txt to GitHub for 100% results.",
            "original_url": request.url
        }

@app.get("/")
def home():
    return {"message": "API is online. For carousels, cookies.txt is highly recommended."}
