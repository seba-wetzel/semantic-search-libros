import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import FastAPI
from main import app as backend_app

# Monta la app FastAPI bajo /api para que coincida con las llamadas del frontend
app = FastAPI()
app.mount("/api", backend_app)
