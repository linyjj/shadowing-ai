
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://linyjj.github.io"
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def video_id_from_url(url):
    match = re.search(
        r"(?:youtu\.be/|youtube\.com/"
        r"(?:watch\?.*?v=|shorts/|embed/))"
        r"([A-Za-z0-9_-]{11})",
        url,
    )
    if not match:
        raise HTTPException(
            status_code=400,
            detail="無效的 YouTube 網址"
        )
    return match.group(1)

@app.get("/")
def home():
    return {"message": "Shadowing API is running"}

@app.get("/transcript")
def transcript(url: str):
    video_id = video_id_from_url(url)

    try:
        api = YouTubeTranscriptApi()
        result = api.fetch(
            video_id,
            languages=["en", "en-US", "en-GB"]
        )

        lines = [
            {
                "text": item.text,
                "start": item.start,
                "duration": item.duration
            }
            for item in result
        ]

        return {
            "video_id": video_id,
            "language": result.language_code,
            "lines": lines
        }

    
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error_type": type(e).__name__,
                "message": "Transcript extraction failed"
            }
        )

