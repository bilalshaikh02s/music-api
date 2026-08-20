import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

CLIENT_ID = "8e233ee421b24258bec154fe5c7977cb"
CLIENT_SECRET = "8e233ee421b24258bec154fe5c7977cb"

app = FastAPI(title="MelodyStream - Spotify Player")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MelodyStream Player</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
        input { padding: 12px; width: 60%; border-radius: 20px; border: none; font-size: 16px; margin-right: 10px; }
        button { padding: 12px 24px; border-radius: 20px; border: none; background: #1db954; color: white; font-weight: bold; cursor: pointer; font-size: 16px; }
        .song-card { background: #181818; margin: 15px auto; padding: 15px; width: 80%; max-width: 500px; border-radius: 12px; text-align: left; }
        iframe { border-radius: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>🎵 MelodyStream Player</h1>
    <div style="margin-bottom: 20px;">
        <input type="text" id="query" placeholder="Search song or artist name...">
        <button onclick="searchSong()">Search</button>
    </div>

    <div id="results"></div>

    <script>
        async function searchSong() {
            const q = document.getElementById('query').value;
            if(!q) return;
            
            const container = document.getElementById('results');
            container.innerHTML = '<p>Searching...</p>';

            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                
                container.innerHTML = '';
                
                if(!data || data.length === 0) {
                    container.innerHTML = '<p>No songs found!</p>';
                    return;
                }

                data.forEach(track => {
                    const div = document.createElement('div');
                    div.className = 'song-card';
                    div.innerHTML = `
                        <h3>${track.name} - ${track.artist}</h3>
                        <iframe src="https://open.spotify.com/embed/track/${track.id}?utm_source=generator&theme=0" 
                                width="100%" height="152" frameBorder="0" allowfullscreen="" 
                                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    `;
                    container.appendChild(div);
                });
            } catch (err) {
                container.innerHTML = '<p style="color: red;">Error fetching songs.</p>';
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.get("/api/search")
def search(q: str = Query(...)):
    try:
        results = sp.search(q=q, limit=5, type='track')
        tracks = []
        for item in results['tracks']['items']:
            tracks.append({
                "id": item['id'],
                "name": item['name'],
                "artist": item['artists'][0]['name']
            })
        return tracks
    except Exception:
        return []