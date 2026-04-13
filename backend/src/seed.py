import time
import requests
from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.openlibrary import search_books
from src.embeddings import embed
from src.translate import translate_to_spanish


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

        description_en = book["description"]

        print(f"  Traduciendo: {book['title'][:60]}...")
        description_es = _with_retry(lambda d=description_en: translate_to_spanish(d))

        print(f"  Embeddeando...")
        vector = _with_retry(lambda d=description_es: embed(d))

        db.table("books").insert({
            **book,
            "description_es": description_es,
            "embedding": vector,
        }).execute()
        inserted += 1

    return {"inserted": inserted, "skipped": skipped, "total_found": len(books)}
