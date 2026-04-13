#!/usr/bin/env python3
"""
Script de seeding standalone.
Uso:
    python seed_books.py                     # queries por defecto
    python seed_books.py --limit 30          # más libros por query
    python seed_books.py --queries "horror" "sci-fi fantasy"  # queries custom
"""
import argparse
import sys
from pathlib import Path

# Permite correr desde el directorio backend sin instalar el paquete
sys.path.insert(0, str(Path(__file__).parent))

from src.seed import seed

DEFAULT_QUERIES = [
    "science fiction",
    "sci-fi space exploration",
    "horror supernatural",
    "horror Stephen King",
    "terror psychological",
    "science fiction dystopia",
]


def main():
    parser = argparse.ArgumentParser(description="Seed de libros en Supabase")
    parser.add_argument(
        "--queries", nargs="+", default=DEFAULT_QUERIES,
        help="Queries a buscar en OpenLibrary"
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Libros a buscar por query (default: 20)"
    )
    args = parser.parse_args()

    total_inserted = 0
    total_skipped = 0

    for query in args.queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        result = seed(query, args.limit)
        total_inserted += result.get("inserted", 0)
        total_skipped += result.get("skipped", 0)
        print(f"  Insertados: {result.get('inserted', 0)} | Salteados: {result.get('skipped', 0)} | Encontrados: {result.get('total_found', 0)}")

    print(f"\n{'='*50}")
    print(f"TOTAL — Insertados: {total_inserted} | Salteados: {total_skipped}")
    print('='*50)


if __name__ == "__main__":
    main()
