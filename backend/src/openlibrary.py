import time
import functools
import requests

BASE_URL = "https://openlibrary.org"

_HEADERS = {
    "User-Agent": "SemanticBookSearch/1.0 (https://github.com/seba-wetzel/semantic-search-libros; contact@semanticbooksearch.app)",
}

_SEARCH_FIELDS = ",".join([
    "key", "title", "author_name", "first_publish_year", "cover_i",
    "number_of_pages_median", "language", "publisher",
    "ratings_average", "ratings_count",
])


def _get(url: str, params: dict = None, timeout: int = 15) -> requests.Response:
    """GET con User-Agent identificatorio."""
    return requests.get(url, params=params, headers=_HEADERS, timeout=timeout)


# Cache en memoria para works y editions ya visitados en esta sesión
@functools.lru_cache(maxsize=2048)
def _fetch_work_cached(book_key: str) -> tuple:
    """Fetches work details and returns (description, subjects_tuple) — cacheable."""
    try:
        resp = _get(f"{BASE_URL}{book_key}.json", timeout=10)
        resp.raise_for_status()
        data = resp.json()

        desc = data.get("description")
        if isinstance(desc, dict):
            description = desc.get("value", "").strip() or None
        elif isinstance(desc, str):
            description = desc.strip() or None
        else:
            description = None

        subjects = tuple(data.get("subjects", []))
        return (description, subjects)
    except Exception:
        return (None, ())


@functools.lru_cache(maxsize=2048)
def _fetch_editions_cached(book_key: str) -> tuple:
    """Fetches first edition for pages/languages/publishers — cacheable."""
    try:
        resp = _get(f"{BASE_URL}{book_key}/editions.json?limit=1", timeout=10)
        if not resp.ok:
            return (None, (), ())
        entries = resp.json().get("entries", [])
        if not entries:
            return (None, (), ())
        e = entries[0]
        pages     = e.get("number_of_pages")
        langs     = tuple(l.get("key", "").split("/")[-1] for l in e.get("languages", []))[:5]
        publishers = tuple(e.get("publishers", []))[:3]
        return (pages, langs, publishers)
    except Exception:
        return (None, (), ())


@functools.lru_cache(maxsize=2048)
def _fetch_ratings_cached(book_key: str) -> tuple:
    """Fetches ratings — cacheable."""
    try:
        resp = _get(f"{BASE_URL}{book_key}/ratings.json", timeout=10)
        if not resp.ok:
            return (None, None)
        summary = resp.json().get("summary", {})
        avg   = summary.get("average")
        count = summary.get("count")
        return (round(avg, 1) if avg else None, count)
    except Exception:
        return (None, None)


def fetch_work_details(book_key: str) -> dict:
    """Obtiene descripción y subjects de un work (con cache)."""
    description, subjects = _fetch_work_cached(book_key)
    return {"description": description, "subjects": list(subjects)}


def search_books(query: str, limit: int = 20) -> list[dict]:
    """Busca libros en OpenLibrary y devuelve los que tienen descripción."""
    print(f"Buscando '{query}' en OpenLibrary...")
    resp = _get(
        f"{BASE_URL}/search.json",
        params={"q": query, "limit": limit, "fields": _SEARCH_FIELDS},
        timeout=20,
    )
    resp.raise_for_status()

    books = []
    for doc in resp.json().get("docs", []):
        key = doc.get("key", "")
        if not key:
            continue

        description, subjects = _fetch_work_cached(key)
        if not description:
            time.sleep(0.2)
            continue

        pages, langs, publishers = _fetch_editions_cached(key)
        rating, rating_count     = _fetch_ratings_cached(key)

        cover_id = doc.get("cover_i")
        extras = {
            "subjects":     list(subjects)[:10],
            "pages":        pages or doc.get("number_of_pages_median"),
            "languages":    list(langs) or doc.get("language", [])[:5],
            "publishers":   list(publishers),
            "rating":       rating,
            "rating_count": rating_count,
        }

        books.append({
            "ol_key":      key,
            "title":       doc.get("title", "Sin título"),
            "author":      ", ".join(doc.get("author_name", ["Desconocido"])),
            "year":        doc.get("first_publish_year"),
            "description": description,
            "cover_url":   f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None,
            "extras":      extras,
        })
        time.sleep(0.2)

    print(f"  {len(books)} libros con descripción encontrados")
    return books
