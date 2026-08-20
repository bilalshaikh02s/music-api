import urllib.parse
import urllib.request
import json
import re
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI(title="MelodyStream - Full Music Player")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MelodyStream - Full Song Player</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
        input { padding: 12px; width: 60%; border-radius: 20px; border: none; font-size: 16px; margin-right: 10px; }
        button { padding: 12px 24px; border-radius: 20px; border: none; background: #1db954; color: white; font-weight: bold; cursor: pointer; font-size: 16px; }
        .song-card { background: #181818; margin: 15px auto; padding: 15px; width: 80%; max-width: 500px; border-radius: 12px; text-align: left; }
        iframe { border-radius: 12px; margin-top: 10px; width: 100%; height: 200px; border: none; }
    </style>
</head>
<body>
    <h1>🎵 MelodyStream (Full Songs)</h1>
    <div style="margin-bottom: 20px;">
        <input type="text" id="query" placeholder="Search full song name...">
        <button onclick="searchSong()">Search</button>
    </div>

    <div id="results"></div>

    <script>
        async function searchSong() {
            const q = document.getElementById('query').value;
            if(!q) return;
            
            const container = document.getElementById('results');
            container.innerHTML = '<p>Searching full songs...</p>';

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
                        <h3 style="margin: 0 0 10px 0;">${track.title}</h3>
                        <iframe src="https://www.youtube.com/embed/${track.video_id}?autoplay=0" allow="autoplay"></iframe>
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
        # Fetching full video audio stream using YouTube search engine
        search_keyword = urllib.parse.quote(q + " full song audio")
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search_keyword}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        
        results = []
        unique_ids = list(dict.fromkeys(video_ids))[:5]
        
        for idx, vid in enumerate(unique_ids):
            results.append({
                "video_id": vid,
                "title": f"Full Song Result {idx+1} for '{q}'"
            })
        return results
    except Exception:
        return []