"""
Backfill extras for existing books.
Fetches subjects, pages, languages, publishers, ratings from OpenLibrary
and updates the extras column — no re-embedding or re-translation needed.
"""
import sys
import time
import requests
from supabase import create_client
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.openlibrary import fetch_work_details

BASE_URL = "https://openlibrary.org"
BATCH = 50  # fetch books in batches


def fetch_search_extras(ol_key: str) -> dict:
    """Fetches page count, languages, publishers, ratings from the works endpoint + editions."""
    extras = {"subjects": [], "pages": None, "languages": [], "publishers": [], "rating": None, "rating_count": None}
    try:
        # Ratings and edition info from works/editions
        editions_url = f"{BASE_URL}{ol_key}/editions.json?limit=1"
        r = requests.get(editions_url, timeout=10)
        if r.ok:
            entries = r.json().get("entries", [])
            if entries:
                e = entries[0]
                extras["pages"] = e.get("number_of_pages")
                langs = e.get("languages", [])
                extras["languages"] = [l.get("key", "").split("/")[-1] for l in langs][:5]
                pubs = e.get("publishers", [])
                extras["publishers"] = pubs[:3]

        # Ratings from works ratings endpoint
        r2 = requests.get(f"{BASE_URL}{ol_key}/ratings.json", timeout=10)
        if r2.ok:
            summary = r2.json().get("summary", {})
            avg = summary.get("average")
            count = summary.get("count")
            if avg:
                extras["rating"] = round(avg, 1)
                extras["rating_count"] = count

    except Exception as e:
        print(f"    warn: {e}")

    return extras


def main():
    db = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch books without extras
    result = db.table("books").select("id, ol_key").is_("extras", "null").execute()
    books = result.data
    total = len(books)
    print(f"Books without extras: {total}")

    if total == 0:
        print("Nothing to backfill.")
        return

    updated = 0
    for i, book in enumerate(books, 1):
        ol_key = book["ol_key"]
        print(f"[{i}/{total}] {ol_key} ...", end=" ", flush=True)

        # Get subjects from work details
        work = fetch_work_details(ol_key)
        search_extras = fetch_search_extras(ol_key)

        extras = {
            "subjects":     work["subjects"][:10] if work["subjects"] else [],
            "pages":        search_extras["pages"],
            "languages":    search_extras["languages"],
            "publishers":   search_extras["publishers"],
            "rating":       search_extras["rating"],
            "rating_count": search_extras["rating_count"],
        }

        db.table("books").update({"extras": extras}).eq("id", book["id"]).execute()
        updated += 1
        print("ok")
        time.sleep(0.4)  # be polite to OpenLibrary

    print(f"\nDone. Updated {updated}/{total} books.")


if __name__ == "__main__":
    main()
