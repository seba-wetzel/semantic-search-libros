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
        "Eres un experto en literatura. El usuario busca libros con estas características:\n"
        f'"{query}"\n\n'
        "Escribe en español un párrafo (3-5 oraciones) que describa los TEMAS, ATMÓSFERA y "
        "ELEMENTOS NARRATIVOS típicos de los libros que coinciden con esa búsqueda. "
        "No inventes una historia concreta ni uses nombres propios de personajes, "
        "organizaciones o lugares. Focalizate en qué hace reconocible a ese tipo de libro: "
        "sus conflictos centrales, el tono, el contexto y los temas filosóficos o sociales "
        "que suele explorar. Escribe solo el párrafo, sin título ni etiquetas."
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
