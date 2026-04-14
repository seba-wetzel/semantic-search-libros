import os
from fastapi import FastAPI, Query, BackgroundTasks, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.embeddings import embed
from src.translate import translate_to_spanish
from src.seed import seed as run_seed
from src.csrf import generate_csrf_token, set_csrf_cookie, verify_csrf, CSRF_HEADER

app = FastAPI(title="Semantic Book Search", version="1.0.0")

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*", CSRF_HEADER],
    allow_credentials=True,
)


def get_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/csrf-token")
def csrf_token():
    """Emite un token CSRF para el frontend."""
    token = generate_csrf_token()
    response = JSONResponse({"csrf_token": token})
    set_csrf_cookie(response, token)
    return response


@app.get("/search")
def search(q: str = Query(..., min_length=2), top: int = Query(5, ge=1, le=20)):
    """Búsqueda semántica de libros por descripción."""
    try:
        query_es = translate_to_spanish(q)
        query_vector = embed(query_es)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error generando embedding: {e}")

    db = get_db()
    result = db.rpc("search_books", {"query_embedding": query_vector, "match_count": top}).execute()
    return {"query": q, "results": result.data}


_SORTABLE_FIELDS = {"title", "author", "year", "created_at"}

@app.get("/books")
def list_books(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
):
    """Lista todos los libros en la base de datos, con orden y paginación."""
    if sort_by not in _SORTABLE_FIELDS:
        raise HTTPException(status_code=400, detail=f"Campo inválido. Opciones: {', '.join(_SORTABLE_FIELDS)}")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Orden inválido. Usar 'asc' o 'desc'.")

    db = get_db()
    result = (
        db.table("books")
        .select("id, ol_key, title, author, year, cover_url, description, description_es")
        .order(sort_by, desc=(order == "desc"))
        .range(offset, offset + limit - 1)
        .execute()
    )
    count = db.table("books").select("id", count="exact").execute()
    return {"total": count.count, "books": result.data}


class SeedRequest(BaseModel):
    query: str = "classic literature"
    limit: int = 20


_seed_status: dict = {"running": False, "last_result": None}


@app.post("/seed", dependencies=[Depends(verify_csrf)])
def seed_books(body: SeedRequest, background_tasks: BackgroundTasks):
    """Inicia el proceso de carga de libros en background."""
    if _seed_status["running"]:
        raise HTTPException(status_code=409, detail="Ya hay un seed en progreso.")

    def run():
        _seed_status["running"] = True
        try:
            _seed_status["last_result"] = run_seed(body.query, body.limit)
        finally:
            _seed_status["running"] = False

    background_tasks.add_task(run)
    return {"message": "Seed iniciado en background.", "query": body.query, "limit": body.limit}


@app.get("/seed/status")
def seed_status():
    return _seed_status
