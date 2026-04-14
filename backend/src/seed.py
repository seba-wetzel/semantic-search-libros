import time
import requests
from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.openlibrary import search_books
from src.embeddings import embed
from src.description import get_description_es


def _with_retry(fn, retries=3, delay=5):
    """Ejecuta fn con reintentos ante errores de Ollama."""
    for attempt in range(retries):
        try:
            return fn()
        except requests.exceptions.HTTPError as e:
            if attempt < retries - 1:
                print(f"  [retry {attempt + 1}/{retries}] Error Ollama: {e}. Esperando {delay}s...")
                time.sleep(delay)
            else:
                raise


def seed(query: str, limit: int) -> dict:
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
    books = search_books(query, limit)

    if not books:
        return {"inserted": 0, "skipped": 0, "total_found": 0}

    inserted, skipped = 0, 0
    for book in books:
        existing = db.table("books").select("id").eq("ol_key", book["ol_key"]).execute()
        if existing.data:
            skipped += 1
            continue

        subjects = (book.get("extras") or {}).get("subjects", [])
        description_es, generated = _with_retry(lambda: get_description_es(
            book["description"], book["title"], book.get("author", ""),
            book.get("year"), subjects,
        ))
        label = "Generando sinopsis" if generated else "Traduciendo"
        print(f"  {label}: {book['title'][:60]}...")

        print(f"  Embeddeando...")
        vector = _with_retry(lambda d=description_es: embed(d))

        db.table("books").insert({
            "ol_key":         book["ol_key"],
            "title":          book["title"],
            "author":         book["author"],
            "year":           book["year"],
            "description":    book["description"],
            "description_es": description_es,
            "cover_url":      book["cover_url"],
            "extras":         book.get("extras"),
            "embedding":      vector,
        }).execute()
        inserted += 1

    return {"inserted": inserted, "skipped": skipped, "total_found": len(books)}
