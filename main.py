import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select

AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

sqlite_file_name = "music.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    artist: str
    album: Optional[str] = "Single"
    file_path: str

app = FastAPI(title="MelodyStream API")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Web page open karne ke liye root route
@app.get("/")
def read_index():
    return FileResponse("index.html")

@app.post("/upload-song", response_model=Song, status_code=201)
async def upload_song(
    title: str = Form(...),
    artist: str = Form(...),
    album: Optional[str] = Form("Single"),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(('.mp3', '.wav', '.m4a')):
        raise HTTPException(status_code=400, detail="Only MP3, WAV, or M4A files allowed!")

    file_location = os.path.join(AUDIO_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    song = Song(title=title, artist=artist, album=album, file_path=file_location)
    with Session(engine) as session:
        session.add(song)
        session.commit()
        session.refresh(song)
        return song

@app.get("/songs", response_model=List[Song])
def get_songs():
    with Session(engine) as session:
        return session.exec(select(Song)).all()

@app.get("/stream/{song_id}")
def stream_song(song_id: int):
    with Session(engine) as session:
        song = session.get(Song, song_id)
        if not song or not os.path.exists(song.file_path):
            raise HTTPException(status_code=404, detail="Audio file missing!")
        return FileResponse(path=song.file_path, media_type="audio/mpeg")