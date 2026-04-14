import requests
from src.config import OLLAMA_CLOUD_URL, OLLAMA_API_KEY, TRANSLATE_MODEL


def generate_hyde_description(query: str) -> str:
    """
    HyDE — Hypothetical Document Embeddings.

    En vez de embeddear la query directamente (señal débil), usamos el LLM
    para generar una sinopsis ficticia del libro ideal. Embeddear ese texto
    produce un vector mucho más similar a las descripciones reales en la DB.
    """
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
