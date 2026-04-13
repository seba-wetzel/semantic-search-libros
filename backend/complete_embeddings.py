#!/usr/bin/env python3
"""
Completa embeddings faltantes (embedding IS NULL).
Uso:
    python complete_embeddings.py
    python complete_embeddings.py --batch 20
"""
import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.embeddings import embed


def _with_retry(fn, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return fn()
        except requests.exceptions.HTTPError as e:
            if attempt < retries - 1:
                print(f"    [retry {attempt + 1}/{retries}] Error Ollama: {e}. Esperando {delay}s...")
                time.sleep(delay)
            else:
                raise


def main():
    parser = argparse.ArgumentParser(description="Completa embeddings faltantes")
    parser.add_argument("--batch", type=int, default=20, help="Libros por lote (default: 20)")
    args = parser.parse_args()

    db = create_client(SUPABASE_URL, SUPABASE_KEY)

    total = db.table("books").select("id", count="exact").is_("embedding", "null").execute().count
    print("Modelo: Cloudflare Workers AI (bge-m3)")
    print(f"Libros sin embedding: {total}\n")

    if total == 0:
        print("Nada por procesar.")
        return

    processed = 0
    errors = 0

    while True:
        rows = (
            db.table("books")
            .select("id, title, description, description_es")
            .is_("embedding", "null")
            .limit(args.batch)
            .execute()
        )
        if not rows.data:
            break

        for book in rows.data:
            try:
                text = book["description_es"] or book["description"]
                print(f"  [{processed + 1}/{total}] {book['title'][:60]}...")
                vector = _with_retry(lambda t=text: embed(t))
                db.table("books").update({"embedding": vector}).eq("id", book["id"]).execute()
                processed += 1
            except Exception as e:
                print(f"    ERROR: {e}")
                errors += 1

    print(f"\nListo — Completados: {processed} | Errores: {errors}")


if __name__ == "__main__":
    main()
