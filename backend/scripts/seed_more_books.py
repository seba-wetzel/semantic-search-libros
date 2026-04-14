"""
Seed masivo de libros por género.
Objetivo: 500+ libros de ciencia ficción, acción/aventura, thriller y terror.

Características:
- Guarda progreso en /tmp/seed_progress.json para poder resumir si se interrumpe
- Reintentos con backoff exponencial por query
- Pausa entre queries para no saturar OpenLibrary
"""
import sys
import json
import time
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.seed import seed

PROGRESS_FILE = pathlib.Path("/tmp/seed_progress.json")

QUERIES = [
    # --- Ciencia ficción ---
    ("hard science fiction",                  40),
    ("space opera science fiction",           40),
    ("cyberpunk dystopian novel",             35),
    ("first contact alien science fiction",   35),
    ("time travel science fiction",           35),
    ("post-apocalyptic science fiction",      35),
    ("science fiction classic novel",         35),
    ("artificial intelligence robot fiction", 30),
    ("galaxy empire interstellar fiction",    30),

    # --- Acción y aventura ---
    ("action adventure survival novel",       35),
    ("spy espionage thriller action",         35),
    ("military war action fiction",           30),
    ("jungle expedition adventure",           25),
    ("treasure hunt adventure novel",         25),
    ("historical adventure fiction",          30),

    # --- Thriller ---
    ("psychological thriller suspense",       40),
    ("crime detective thriller novel",        40),
    ("legal courtroom thriller",              30),
    ("political conspiracy thriller",         30),
    ("medical thriller fiction",              25),
    ("serial killer thriller mystery",        35),

    # --- Terror ---
    ("horror supernatural novel",             40),
    ("psychological horror fiction",          35),
    ("gothic horror classic",                 30),
    ("supernatural monster horror",           30),
    ("haunted house horror novel",            25),
    ("cosmic horror lovecraftian",            25),
]


def load_progress() -> set:
    """Devuelve el set de queries ya completadas."""
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text())
        return set(data.get("completed", []))
    return set()


def save_progress(completed: set):
    PROGRESS_FILE.write_text(json.dumps({"completed": list(completed)}, indent=2))


def seed_with_retry(query: str, limit: int, max_attempts: int = 4) -> dict | None:
    """Ejecuta seed con backoff exponencial. Devuelve None si todos los intentos fallan."""
    for attempt in range(max_attempts):
        try:
            return seed(query, limit)
        except Exception as e:
            wait = 15 * (2 ** attempt)  # 15s, 30s, 60s, 120s
            if attempt < max_attempts - 1:
                print(f"  intento {attempt+1}/{max_attempts} falló: {e}")
                print(f"  esperando {wait}s antes de reintentar...")
                time.sleep(wait)
            else:
                print(f"  todos los intentos fallaron: {e}")
    return None


def main():
    completed = load_progress()
    pending = [(q, l) for q, l in QUERIES if q not in completed]

    if not pending:
        print("Todas las queries ya completadas. Borrá /tmp/seed_progress.json para reiniciar.")
        return

    print(f"Queries completadas: {len(completed)}/{len(QUERIES)}")
    print(f"Queries pendientes:  {len(pending)}\n")

    total_inserted = 0
    total_skipped  = 0

    for i, (query, limit) in enumerate(pending, 1):
        idx = QUERIES.index((query, limit)) + 1
        print(f"[{idx}/{len(QUERIES)}] '{query}' (limit {limit})")

        result = seed_with_retry(query, limit)

        if result is not None:
            total_inserted += result["inserted"]
            total_skipped  += result["skipped"]
            print(f"  → insertados: {result['inserted']}  saltados: {result['skipped']}  encontrados: {result['total_found']}")
            completed.add(query)
            save_progress(completed)
        else:
            print(f"  SKIP permanente: '{query}'")

        # Pausa entre queries para no saturar OpenLibrary
        if i < len(pending):
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"Total insertados: {total_inserted}")
    print(f"Total saltados (duplicados): {total_skipped}")
    print(f"Queries completadas: {len(completed)}/{len(QUERIES)}")

    if len(completed) == len(QUERIES):
        PROGRESS_FILE.unlink(missing_ok=True)
        print("Seed completo. Archivo de progreso eliminado.")


if __name__ == "__main__":
    main()
