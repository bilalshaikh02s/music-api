import urllib.parse
import urllib.request
import json
import re
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
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
        input { padding: 12px 20px; width: 55%; border-radius: 20px; border: none; font-size: 16px; outline: none; }
        button { padding: 12px 24px; border-radius: 20px; border: none; background: #1db954; color: white; font-weight: bold; cursor: pointer; font-size: 16px; margin-left: 10px; }
        button:hover { background: #1ed760; }
        .song-card { background: #181818; margin: 15px auto; padding: 15px; width: 85%; max-width: 500px; border-radius: 12px; text-align: left; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .song-card h3 { margin: 0 0 10px 0; color: #1db954; font-size: 18px; text-transform: capitalize; }
        .player-wrapper { position: relative; width: 100%; height: 80px; overflow: hidden; border-radius: 8px; background: #282828; }
        iframe { width: 100%; height: 200px; border: none; margin-top: -60px; }
    </style>
</head>
<body>
    <h1>🎵 MelodyStream Player</h1>
    <div style="margin-bottom: 25px;">
        <input type="text" id="query" placeholder="Search song or artist name...">
        <button onclick="searchSong()">Search</button>
    </div>

    <div id="results"></div>

    <script>
        async function searchSong() {
            const q = document.getElementById('query').value;
            if(!q) return;
            
            const container = document.getElementById('results');
            container.innerHTML = '<p style="color: #b3b3b3;">Searching song...</p>';

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
                        <h3>🎵 ${track.title}</h3>
                        <div class="player-wrapper">
                            <iframe src="https://www.youtube.com/embed/${track.video_id}?autoplay=0" allow="autoplay"></iframe>
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
        search_keyword = urllib.parse.quote(q + " full song audio")
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search_keyword}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        
        results = []
        unique_ids = list(dict.fromkeys(video_ids))[:5]
        
        for vid in unique_ids:
            results.append({
                "video_id": vid,
                "title": q
            })
        return results
    except Exception:
        return []