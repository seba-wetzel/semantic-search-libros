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
        "Eres un experto en literatura. El usuario busca un libro con estas características:\n"
        f'"{query}"\n\n'
        "Escribe en español una sinopsis detallada (4-6 oraciones) de un libro ficticio que "
        "coincida perfectamente con esa búsqueda. "
        "Escribe solo la sinopsis, sin título, sin autor, sin comillas, sin etiquetas."
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
