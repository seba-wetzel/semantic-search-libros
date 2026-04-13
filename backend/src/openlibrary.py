import requests
import time

BASE_URL = "https://openlibrary.org"


def search_books(query: str, limit: int = 20) -> list[dict]:
    """Busca libros en OpenLibrary y devuelve los que tienen descripci├│n."""
    print(f"Buscando '{query}' en OpenLibrary...")
    resp = requests.get(
        f"{BASE_URL}/search.json",
        params={"q": query, "limit": limit, "fields": "key,title,author_name,first_publish_year,cover_i"},
    )
    resp.raise_for_status()

    books = []
    for doc in resp.json().get("docs", []):
        key = doc.get("key", "")
        description = fetch_description(key)
        if not description:
            continue

        cover_id = doc.get("cover_i")
        books.append({
            "ol_key": key,
            "title": doc.get("title", "Sin t├¡tulo"),
            "author": ", ".join(doc.get("author_name", ["Desconocido"])),
            "year": doc.get("first_publish_year"),
            "description": description,
            "cover_url": f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None,
        })
        time.sleep(0.3)

    print(f"  {len(books)} libros con descripci├│n encontrados")
    return books


def fetch_description(book_key: str) -> str | None:
    """Obtiene la descripci├│n de un libro dado su key."""
    try:
        resp = requests.get(f"{BASE_URL}{book_key}.json", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        desc = data.get("description")
        if isinstance(desc, dict):
            return desc.get("value", "").strip() or None
        if isinstance(desc, str):
            return desc.strip() or None
        return None
    except Exception:
        return None
