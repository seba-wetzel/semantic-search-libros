import os
from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str = None) -> str:
    val = os.environ[key] if default is None else os.getenv(key, default)
    return val.strip() if val else val


SUPABASE_URL = _env("SUPABASE_URL")
SUPABASE_KEY = _env("SUPABASE_KEY")
OLLAMA_URL = _env("OLLAMA_URL", "http://localhost:11434")
CLOUDFLARE_ACCOUNT_ID = _env("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = _env("CLOUDFLARE_API_TOKEN")
TRANSLATE_MODEL = _env("TRANSLATE_MODEL", "gemma3:12b")
OLLAMA_CLOUD_URL = _env("OLLAMA_CLOUD_URL", "https://ollama.com")
OLLAMA_API_KEY = _env("OLLAMA_API_KEY", "")
