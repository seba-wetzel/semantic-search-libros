"""
Enriquecimiento de descripciones pobres.

OpenLibrary no siempre tiene un resumen del argumento — puede ser una nota editorial,
una fecha de publicación, o simplemente texto irrelevante.

Este script detecta esas descripciones y las reemplaza con una sinopsis generada por el
LLM usando los metadatos confiables del libro (título, autor, año, subjects).
También regenera el embedding a partir de la sinopsis nueva.
"""
import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.embeddings import embed
from src.description import is_poor, generate_synopsis


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    db = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Traer todos los libros paginando (Supabase limita 1000 por request)
    print("Cargando libros...")
    books = []
    page_size = 1000
    offset = 0
    while True:
        batch = db.table("books").select("id, title, author, year, description, extras") \
            .range(offset, offset + page_size - 1).execute()
        books.extend(batch.data)
        if len(batch.data) < page_size:
            break
        offset += page_size
    print(f"Total libros: {len(books)}")

    poor = [b for b in books if is_poor(b.get("description", ""))]
    print(f"Descripciones pobres detectadas: {len(poor)}")

    if not poor:
        print("Nada que enriquecer.")
        return

    enriched = 0
    errors = 0

    for i, book in enumerate(poor, 1):
        subjects = (book.get("extras") or {}).get("subjects", [])
        print(f"[{i}/{len(poor)}] {book['title'][:60]} ...", end=" ", flush=True)

        for attempt in range(3):
            try:
                synopsis = generate_synopsis(
                    book["title"],
                    book.get("author", "Desconocido"),
                    book.get("year"),
                    subjects,
                )
                vector = embed(synopsis)

                db.table("books").update({
                    "description_es": synopsis,
                    "embedding": vector,
                }).eq("id", book["id"]).execute()

                print(f"ok ({len(synopsis)} chars)")
                enriched += 1
                break
            except Exception as e:
                if attempt < 2:
                    print(f"retry {attempt+1}...", end=" ", flush=True)
                    time.sleep(10)
                else:
                    print(f"ERROR: {e}")
                    errors += 1

        time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"Enriquecidos: {enriched}")
    print(f"Errores:      {errors}")
    print(f"Sin cambios:  {len(books) - len(poor)}")


if __name__ == "__main__":
    main()
