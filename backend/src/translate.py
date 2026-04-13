import requests
from src.config import OLLAMA_CLOUD_URL, OLLAMA_API_KEY, TRANSLATE_MODEL


def translate_to_spanish(text: str) -> str:
    """Traduce texto al español usando Ollama Cloud (OpenAI-compatible endpoint)."""
    prompt = f"Translate the following text to Spanish. Output only the translation, no explanations:\n\n{text}"
    response = requests.post(
        f"{OLLAMA_CLOUD_URL}/v1/chat/completions",
        headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
        json={
            "model": TRANSLATE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()
