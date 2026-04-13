#!/usr/bin/env python3
"""
Migra libros existentes sin description_es: traduce y re-genera el embedding.
Uso:
    python migrate_translations.py
    python migrate_translations.py --batch 10   # procesar de a N libros
"""
import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.translate import translate_to_spanish
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
    parser = argparse.ArgumentParser(description="Migra traducciones de libros existentes")
    parser.add_argument("--batch", type=int, default=20, help="Libros por lote (default: 20)")
    args = parser.parse_args()

    db = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Contar pendientes
    count = db.table("books").select("id", count="exact").is_("description_es", "null").execute()
    total = count.count
    print(f"Libros sin traducción: {total}")

    if total == 0:
        print("Nada por migrar.")
        return

    processed = 0
    errors = 0
    offset = 0

    while True:
        rows = (
            db.table("books")
            .select("id, title, description")
            .is_("description_es", "null")
            .range(offset, offset + args.batch - 1)
            .execute()
        )
        if not rows.data:
            break

        for book in rows.data:
            try:
                print(f"  [{processed + 1}/{total}] {book['title'][:60]}...")
                description_es = _with_retry(lambda d=book["description"]: translate_to_spanish(d))
                vector = _with_retry(lambda d=description_es: embed(d))
                db.table("books").update({
                    "description_es": description_es,
                    "embedding": vector,
                }).eq("id", book["id"]).execute()
                processed += 1
            except Exception as e:
                print(f"    ERROR: {e}")
                errors += 1

        offset += args.batch

    print(f"\nMigración completa — Procesados: {processed} | Errores: {errors}")


if __name__ == "__main__":
    main()
