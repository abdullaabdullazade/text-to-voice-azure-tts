from fastapi import FastAPI
import edge_tts
from uuid import uuid4
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles


class TTSRequest(BaseModel):
    text: str
    voice: str


class TTSDeleteRequest(BaseModel):
    filename: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")

templates = Jinja2Templates(directory="frontend")


async def text_to_speech(text, voice):

    try:
        filename_base = f"audio/{uuid4()}"
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(f"{filename_base}.ogg")
        return f"{filename_base}.ogg"
    except Exception as e:
        return None


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})


@app.post("/api/tts")
async def audio_link(body: TTSRequest):
    text = body.text
    voice = body.voice
    os.makedirs("audio", exist_ok=True)
    audio_link = await text_to_speech(text, voice)
    return {"audio_link": audio_link}


@app.delete("/api/delete")
async def delete_audio(body: TTSDeleteRequest):
    filename = body.filename
    try:
        os.remove(filename)
        return {"message": "File deleted "}
    except Exception as e:
        return {"error": str(e)}
