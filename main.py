from yt_dlp import YoutubeDL
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_video_url")
def get_video_url(url: str, quality: str = "best"):
    ydl_opts = {
        'quiet': True,
        'format': quality,
        'skip_download': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "success": True,
                "video_url": info.get("url")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
