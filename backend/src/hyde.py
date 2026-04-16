import re
import requests
from supabase import create_client
from src.config import OLLAMA_CLOUD_URL, OLLAMA_API_KEY, TRANSLATE_MODEL, SUPABASE_URL, SUPABASE_KEY


def _normalize(query: str) -> str:
    """Normaliza la query para usarla como cache key."""
    return re.sub(r'\s+', ' ', query.strip().lower())


def _get_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _llm_generate(query: str) -> str:
    prompt = (
        "El usuario busca libros con estas características: "
        f'"{query}"\n\n'
        "Escribí en español UNA sola oración que identifique: género literario, "
        "época o contexto, y tema o conflicto central. "
        "Sin adjetivos, sin narrativa, sin inventar detalles. "
        "Solo los datos esenciales, como una etiqueta de catálogo."
    )
    response = requests.post(
        f"{OLLAMA_CLOUD_URL}/v1/chat/completions",
        headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
        json={
            "model": TRANSLATE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def generate_hyde_description(query: str) -> str:
    """
    HyDE — Hypothetical Document Embeddings.
    Usa la DB como cache: si la query ya fue procesada, devuelve el resultado guardado.
    """
    key = _normalize(query)
    db = _get_db()

    # Intentar leer del cache
    cached = db.table("hyde_cache").select("hyde_description").eq("query_normalized", key).limit(1).execute()
    if cached.data:
        print(f"  [hyde cache hit] '{key}'")
        return cached.data[0]["hyde_description"]

    # Generar con LLM y guardar en cache
    print(f"  [hyde generating] '{key}'")
    description = _llm_generate(query)
    db.table("hyde_cache").upsert({
        "query_normalized": key,
        "hyde_description": description,
    }).execute()

    return description
