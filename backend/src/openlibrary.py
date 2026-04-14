import requests
import time

BASE_URL = "https://openlibrary.org"

_SEARCH_FIELDS = ",".join([
    "key", "title", "author_name", "first_publish_year", "cover_i",
    "number_of_pages_median", "language", "publisher",
    "ratings_average", "ratings_count",
])


def search_books(query: str, limit: int = 20) -> list[dict]:
    """Busca libros en OpenLibrary y devuelve los que tienen descripción."""
    print(f"Buscando '{query}' en OpenLibrary...")
    resp = requests.get(
        f"{BASE_URL}/search.json",
        params={"q": query, "limit": limit, "fields": _SEARCH_FIELDS},
        timeout=15,
    )
    resp.raise_for_status()

    books = []
    for doc in resp.json().get("docs", []):
        key = doc.get("key", "")
        work = fetch_work_details(key)
        if not work["description"]:
            continue

        cover_id = doc.get("cover_i")

        publishers = doc.get("publisher", [])
        extras = {
            "subjects":     work["subjects"][:10] if work["subjects"] else [],
            "pages":        doc.get("number_of_pages_median"),
            "languages":    doc.get("language", [])[:5],
            "publishers":   publishers[:3] if publishers else [],
            "rating":       round(doc["ratings_average"], 1) if doc.get("ratings_average") else None,
            "rating_count": doc.get("ratings_count"),
        }

        books.append({
            "ol_key":    key,
            "title":     doc.get("title", "Sin título"),
            "author":    ", ".join(doc.get("author_name", ["Desconocido"])),
            "year":      doc.get("first_publish_year"),
            "description": work["description"],
            "cover_url": f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None,
            "extras":    extras,
        })
        time.sleep(0.3)

    print(f"  {len(books)} libros con descripción encontrados")
    return books


def fetch_work_details(book_key: str) -> dict:
    """Obtiene descripción y datos extra de un libro dado su key de work."""
    empty = {"description": None, "subjects": []}
    try:
        resp = requests.get(f"{BASE_URL}{book_key}.json", timeout=10)
        resp.raise_for_status()
        data = resp.json()

        desc = data.get("description")
        if isinstance(desc, dict):
            description = desc.get("value", "").strip() or None
        elif isinstance(desc, str):
            description = desc.strip() or None
        else:
            description = None

        subjects = data.get("subjects", [])

        return {"description": description, "subjects": subjects}
    except Exception:
        return empty
