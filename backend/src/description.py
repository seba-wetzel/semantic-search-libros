"""
Genera o mejora descripciones de libros para uso en embeddings.

Si la descripción de OpenLibrary es pobre (corta, nota editorial, etc.),
genera una sinopsis en español directamente con el LLM usando los metadatos
confiables del libro (título, autor, año, subjects).
"""
import re
import requests
from src.config import OLLAMA_CLOUD_URL, OLLAMA_API_KEY, TRANSLATE_MODEL
from src.translate import translate_to_spanish

MIN_LENGTH = 200

_BAD_PATTERNS = re.compile("|".join([
    r"first published",
    r"originally published",
    r"published by",
    r"bantam book",
    r"includes index",
    r"hardcover|paperback|softcover",
    r"\bisbn\b",
    r"all rights reserved",
    r"copyright",
    r"translated (from|by)",
    r"edition\b",
    r"^\s*\d{4}\s*$",
]), re.IGNORECASE)


def is_poor(description: str) -> bool:
    if not description or len(description.strip()) < MIN_LENGTH:
        return True
    if _BAD_PATTERNS.search(description):
        return True
    return False


def generate_synopsis(title: str, author: str, year: int | None, subjects: list[str]) -> str:
    """Genera una sinopsis en español usando el LLM a partir de los metadatos."""
    subjects_str = ", ".join(subjects[:8]) if subjects else "no disponibles"
    year_str = str(year) if year else "desconocido"

    prompt = (
        f"Escribe en español un resumen del argumento del libro '{title}' "
        f"de {author} (publicado en {year_str}). "
        f"Temas relacionados: {subjects_str}. "
        "Describe en 3-4 oraciones quiénes son los protagonistas, qué problema o conflicto "
        "enfrentan y en qué contexto ocurre la historia. "
        "Sé concreto y no uses frases genéricas. "
        "Escribe solo el resumen, sin título ni encabezado."
    )
    response = requests.post(
        f"{OLLAMA_CLOUD_URL}/v1/chat/completions",
        headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
        json={
            "model": TRANSLATE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def get_description_es(description: str, title: str, author: str,
                       year: int | None, subjects: list[str]) -> tuple[str, bool]:
    """
    Devuelve (description_es, was_generated).
    Si la descripción original es pobre, genera una sinopsis con el LLM.
    Si es buena, traduce al español normalmente.
    """
    if is_poor(description):
        return generate_synopsis(title, author, year, subjects), True
    return translate_to_spanish(description), False
