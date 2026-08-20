import urllib.parse
import urllib.request
import json
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI(title="MelodyStream Player")

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
        .song-card { background: #181818; margin: 15px auto; padding: 15px; width: 80%; max-width: 500px; border-radius: 12px; text-align: left; display: flex; align-items: center; gap: 15px; }
        .song-card img { border-radius: 8px; width: 80px; height: 80px; object-fit: cover; }
        .song-info { flex: 1; }
        audio { width: 100%; margin-top: 10px; }
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
                        <img src="${track.image}" alt="cover">
                        <div class="song-info">
                            <h3 style="margin:0 0 5px 0; font-size: 16px;">${track.name}</h3>
                            <p style="margin:0; color: #b3b3b3; font-size: 14px;">${track.artist}</p>
                            <audio controls src="${track.preview_url}"></audio>
                        </div>
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
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=song&limit=6"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            results = []
            for item in res_data.get('results', []):
                results.append({
                    "name": item.get("trackName"),
                    "artist": item.get("artistName"),
                    "preview_url": item.get("previewUrl"),
                    "image": item.get("artworkUrl100")
                })
            return results
    except Exception as e:
        return []