"""
Seed masivo de libros por género.
Objetivo: 500+ libros de ciencia ficción, acción/aventura, thriller y terror.
Usa el seeder existente que maneja deduplicación por ol_key.
"""
import sys
import time
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))

from src.seed import seed

QUERIES = [
    # --- Ciencia ficción ---
    ("hard science fiction",              40),
    ("space opera science fiction",       40),
    ("cyberpunk dystopian novel",         35),
    ("first contact alien science fiction", 35),
    ("time travel science fiction",       35),
    ("post-apocalyptic science fiction",  35),
    ("science fiction classic novel",     35),
    ("artificial intelligence robot fiction", 30),
    ("galaxy empire interstellar fiction", 30),

    # --- Acción y aventura ---
    ("action adventure survival novel",   35),
    ("spy espionage thriller action",     35),
    ("military war action fiction",       30),
    ("jungle expedition adventure",       25),
    ("treasure hunt adventure novel",     25),
    ("historical adventure fiction",      30),

    # --- Thriller ---
    ("psychological thriller suspense",   40),
    ("crime detective thriller novel",    40),
    ("legal courtroom thriller",          30),
    ("political conspiracy thriller",     30),
    ("medical thriller fiction",          25),
    ("serial killer thriller mystery",    35),

    # --- Terror ---
    ("horror supernatural novel",         40),
    ("psychological horror fiction",      35),
    ("gothic horror classic",             30),
    ("supernatural monster horror",       30),
    ("haunted house horror novel",        25),
    ("cosmic horror lovecraftian",        25),
]


def main():
    total_inserted = 0
    total_skipped = 0

    for i, (query, limit) in enumerate(QUERIES, 1):
        print(f"\n[{i}/{len(QUERIES)}] Query: '{query}' (limit {limit})")
        for attempt in range(3):
            try:
                result = seed(query, limit)
                total_inserted += result["inserted"]
                total_skipped  += result["skipped"]
                print(f"  → insertados: {result['inserted']}  saltados: {result['skipped']}  encontrados: {result['total_found']}")
                break
            except Exception as e:
                print(f"  intento {attempt+1}/3 falló: {e}")
                if attempt < 2:
                    time.sleep(10)
                else:
                    print(f"  SKIP: {query}")

        # Pausa entre queries para no saturar OpenLibrary
        if i < len(QUERIES):
            time.sleep(2)

    print(f"\n{'='*50}")
    print(f"Total insertados: {total_inserted}")
    print(f"Total saltados (duplicados): {total_skipped}")


if __name__ == "__main__":
    main()
