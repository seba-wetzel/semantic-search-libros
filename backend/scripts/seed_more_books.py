"""
Seed masivo de libros por género.
Objetivo: 1000+ libros en la base de datos.
Guarda progreso en /tmp/seed_progress.json para poder resumir si se interrumpe.
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
    ("hard science fiction",                      40),
    ("space opera science fiction",               40),
    ("cyberpunk dystopian novel",                 35),
    ("first contact alien science fiction",       35),
    ("time travel science fiction",               35),
    ("post-apocalyptic science fiction",          35),
    ("science fiction classic novel",             35),
    ("artificial intelligence robot fiction",     30),
    ("galaxy empire interstellar fiction",        30),
    ("mars colonization science fiction",         30),
    ("virtual reality simulation fiction",        30),
    ("genetic engineering biotech fiction",       30),
    ("climate change environmental fiction",      30),
    ("parallel universe alternate history",       30),
    ("underwater ocean science fiction",          25),
    ("generation ship colonization fiction",      25),
    ("alien invasion war science fiction",        30),
    ("dystopian society government control",      35),
    ("nanotechnology future science fiction",     25),
    ("science fiction anthology short stories",   30),
    ("solarpunk utopian science fiction",         25),
    ("space exploration astronaut fiction",       30),

    # --- Acción y aventura ---
    ("action adventure survival novel",           35),
    ("spy espionage thriller action",             35),
    ("military war action fiction",               30),
    ("jungle expedition adventure",               25),
    ("treasure hunt adventure novel",             25),
    ("historical adventure fiction",              30),
    ("pirate sea adventure novel",                25),
    ("ancient civilization archaeology adventure",30),
    ("heist crime action thriller",               30),
    ("mercenary soldier action fiction",          25),
    ("extreme survival wilderness fiction",       25),
    ("ancient rome greece historical fiction",    30),
    ("viking medieval adventure fiction",         25),
    ("ninja samurai martial arts fiction",        25),
    ("western frontier cowboy adventure",         25),
    ("underwater deep sea adventure",             20),

    # --- Thriller ---
    ("psychological thriller suspense",           40),
    ("crime detective thriller novel",            40),
    ("legal courtroom thriller",                  30),
    ("political conspiracy thriller",             30),
    ("medical thriller fiction",                  25),
    ("serial killer thriller mystery",            35),
    ("financial economic thriller",               25),
    ("hacker cyber technology thriller",          25),
    ("missing person abduction thriller",         35),
    ("domestic thriller marriage suspense",       35),
    ("cold war spy espionage thriller",           30),
    ("forensic pathology crime thriller",         30),
    ("journalist investigation thriller",         25),
    ("terrorism hostage thriller",                25),
    ("cozy mystery small town detective",         25),
    ("noir detective hardboiled fiction",         30),
    ("police procedural crime novel",             35),

    # --- Terror ---
    ("horror supernatural novel",                 40),
    ("psychological horror fiction",              35),
    ("gothic horror classic",                     30),
    ("supernatural monster horror",               30),
    ("haunted house ghost horror novel",          25),
    ("cosmic horror lovecraftian",                25),
    ("zombie apocalypse horror fiction",          30),
    ("demonic possession occult horror",          25),
    ("slasher killer horror fiction",             25),
    ("body horror transformation fiction",        20),
    ("vampire horror classic novel",              30),
    ("werewolf shapeshifter horror",              20),
    ("witch coven dark magic horror",             25),
    ("folk horror rural darkness",                20),
    ("haunted asylum horror fiction",             20),
    ("Stephen King horror thriller",              35),
]


def load_progress() -> set:
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text())
        return set(data.get("completed", []))
    return set()


def save_progress(completed: set):
    PROGRESS_FILE.write_text(json.dumps({"completed": list(completed)}, indent=2))


def seed_with_retry(query: str, limit: int, max_attempts: int = 4) -> dict | None:
    for attempt in range(max_attempts):
        try:
            return seed(query, limit)
        except Exception as e:
            wait = 15 * (2 ** attempt)  # 15s, 30s, 60s, 120s
            if attempt < max_attempts - 1:
                print(f"  intento {attempt+1}/{max_attempts} falló: {e}")
                print(f"  esperando {wait}s...")
                time.sleep(wait)
            else:
                print(f"  todos los intentos fallaron: {e}")
    return None


def main():
    completed = load_progress()
    pending = [(q, l) for q, l in QUERIES if q not in completed]

    print(f"Queries completadas: {len(completed)}/{len(QUERIES)}")
    print(f"Queries pendientes:  {len(pending)}\n")

    if not pending:
        print("Todo completado. Borrá /tmp/seed_progress.json para reiniciar.")
        return

    total_inserted = 0
    total_skipped  = 0

    for i, (query, limit) in enumerate(pending, 1):
        idx = next(j+1 for j, (q, _) in enumerate(QUERIES) if q == query)
        print(f"[{idx}/{len(QUERIES)}] '{query}' (limit {limit})")

        result = seed_with_retry(query, limit)

        if result is not None:
            total_inserted += result["inserted"]
            total_skipped  += result["skipped"]
            print(f"  → insertados: {result['inserted']}  saltados: {result['skipped']}  encontrados: {result['total_found']}")
            completed.add(query)
            save_progress(completed)
        else:
            print(f"  SKIP: '{query}'")

        if i < len(pending):
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"Total insertados en esta sesión: {total_inserted}")
    print(f"Total saltados (duplicados):     {total_skipped}")
    print(f"Queries completadas: {len(completed)}/{len(QUERIES)}")

    if len(completed) == len(QUERIES):
        PROGRESS_FILE.unlink(missing_ok=True)
        print("Seed completo.")


if __name__ == "__main__":
    main()
