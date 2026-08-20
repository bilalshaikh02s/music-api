import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

CLIENT_ID = "8e233ee421b24258bec154fe5c7977cb"

app = FastAPI(title="MelodyStream - Spotify Player")

HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MelodyStream Player</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }}
        input {{ padding: 10px; width: 60%; border-radius: 20px; border: none; font-size: 16px; }}
        button {{ padding: 10px 20px; border-radius: 20px; border: none; background: #1db954; color: white; font-weight: bold; cursor: pointer; }}
        .song-card {{ background: #181818; margin: 15px auto; padding: 15px; width: 80%; max-width: 500px; border-radius: 8px; text-align: left; }}
        iframe {{ border-radius: 12px; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>🎵 MelodyStream Player</h1>
    <input type="text" id="query" placeholder="Search song or artist name...">
    <button onclick="searchSong()">Search</button>

    <div id="results"></div>

    <script>
        async function searchSong() {{
            const q = document.getElementById('query').value;
            if(!q) return;
            
            const res = await fetch(`/api/search?q=${{encodeURIComponent(q)}}`);
            const data = await res.json();
            
            const container = document.getElementById('results');
            container.innerHTML = '';
            
            data.forEach(track => {{
                const div = document.createElement('div');
                div.className = 'song-card';
                div.innerHTML = `
                    <h3>${{track.name}} - ${{track.artist}}</h3>
                    <iframe src="https://open.spotify.com/embed/track/${{track.id}}?utm_source=generator&theme=0" 
                            width="100%" height="152" frameBorder="0" allowfullscreen="" 
                            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                `;
                container.appendChild(div);
            }});
        }}
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.get("/api/search")
def search(q: str = Query(...)):
    # Basic search via public API endpoint
    import urllib.request
    import json
    
    url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(q)}&type=track&limit=5"
    # Public token handler
    return []