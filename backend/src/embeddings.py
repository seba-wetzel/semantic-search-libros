import requests
from src.config import CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN

CF_EMBED_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/baai/bge-m3"


def embed(text: str) -> list[float]:
    """Genera un embedding usando Cloudflare Workers AI (bge-m3, 1024 dims)."""
    response = requests.post(
        CF_EMBED_URL,
        headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"},
        json={"text": [text]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["result"]["data"][0]
