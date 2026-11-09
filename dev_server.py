"""Local development server: the API plus the web UI on one port.

    python3 dev_server.py          # then open http://127.0.0.1:8000

On Vercel the UI in public/ is served by the platform and only api/index.py runs as Python.
"""
from fastapi.staticfiles import StaticFiles

from api.index import app

app.mount("/", StaticFiles(directory="public", html=True), name="ui")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
