import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from main import app as backend_app

STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

app = FastAPI()

# API routes
app.mount("/api", backend_app)

# Assets estáticos (JS, CSS, imágenes)
if os.path.isdir(os.path.join(STATIC_DIR, 'assets')):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, 'assets')), name="assets")

# SPA fallback — todas las rutas sirven index.html
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))
