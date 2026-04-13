#!/usr/bin/env python3
"""
Traduce y re-embeddea solo los libros sin description_es.
Uso:
    python fix_missing_translations.py
"""
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.translate import translate_to_spanish
from src.embeddings import embed

MISSING_IDS = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 61, 64, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 108, 109, 110, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 131, 132, 133, 134, 135, 136, 137, 138]


def _with_retry(fn, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return fn()
        except requests.exceptions.HTTPError as e:
            if attempt < retries - 1:
                print(f"    [retry {attempt + 1}/{retries}] Error: {e}. Esperando {delay}s...")
                time.sleep(delay)
            else:
                raise


def main():
    db = create_client(SUPABASE_URL, SUPABASE_KEY)

    rows = (
        db.table("books")
        .select("id, title, description")
        .in_("id", MISSING_IDS)
        .is_("description_es", "null")
        .execute()
    )

    total = len(rows.data)
    print(f"Libros a procesar: {total}")
    print("Modelo embedding: Cloudflare Workers AI (bge-m3)\n")

    if total == 0:
        print("Nada por procesar.")
        return

    translated = 0
    errors = 0

    for i, book in enumerate(rows.data, 1):
        try:
            print(f"  [{i}/{total}] {book['title'][:60]}...")

            description_es = _with_retry(lambda d=book["description"]: translate_to_spanish(d))
            vector = _with_retry(lambda d=description_es: embed(d))

            db.table("books").update({
                "description_es": description_es,
                "embedding": vector,
            }).eq("id", book["id"]).execute()

            translated += 1
        except Exception as e:
            print(f"    ERROR: {e}")
            errors += 1

    print(f"\nListo — Traducidos y embeddeados: {translated} | Errores: {errors}")


if __name__ == "__main__":
    main()
