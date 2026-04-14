"""
Enriquecimiento de descripciones pobres.

OpenLibrary no siempre tiene un resumen del argumento — puede ser una nota editorial,
una fecha de publicación, o simplemente texto irrelevante.

Este script detecta esas descripciones y las reemplaza con una sinopsis generada por el
LLM usando los metadatos confiables del libro (título, autor, año, subjects).
También regenera el embedding a partir de la sinopsis nueva.
"""
import re
import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY, OLLAMA_CLOUD_URL, OLLAMA_API_KEY, TRANSLATE_MODEL
from src.embeddings import embed
import requests

# ── Heurísticas para detectar descripciones pobres ──────────────────────────

MIN_LENGTH = 200  # menos de esto casi nunca es un resumen útil

BAD_PATTERNS = [
    r"first published",
    r"originally published",
    r"published by",
    r"bantam book",
    r"includes index",
    r"a novel by",
    r"^\s*\d{4}\s*$",          # solo un año
    r"^[^.]{0,60}$",           # una sola frase muy corta sin punto
    r"edition\b",
    r"hardcover|paperback|softcover",
    r"isbn",
    r"all rights reserved",
    r"copyright",
    r"translated (from|by)",
]

BAD_RE = re.compile("|".join(BAD_PATTERNS), re.IGNORECASE)


def is_poor(description: str) -> bool:
    if not description or len(description.strip()) < MIN_LENGTH:
        return True
    if BAD_RE.search(description):
        return True
    return False


# ── Generación de sinopsis con LLM ──────────────────────────────────────────

def generate_synopsis(title: str, author: str, year: int | None, subjects: list[str]) -> str:
    subjects_str = ", ".join(subjects[:8]) if subjects else "no disponibles"
    year_str = str(year) if year else "desconocido"

    prompt = (
        f"Escribe en español un resumen del argumento del libro '{title}' "
        f"de {author} (publicado en {year_str}). "
        f"Temas relacionados: {subjects_str}. "
        "Describe en 3-4 oraciones quiénes son los protagonistas, qué problema o conflicto "
        "enfrentan y en qué contexto ocurre la historia. "
        "Sé concreto y no uses frases genéricas. "
        "Escribe solo el resumen, sin título ni encabezado."
    )

    response = requests.post(
        f"{OLLAMA_CLOUD_URL}/v1/chat/completions",
        headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
        json={
            "model": TRANSLATE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


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
