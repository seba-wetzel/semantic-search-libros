# Semantic Search Libros

Buscador semántico de libros en español. Ingresás una idea, concepto o frase y el sistema encuentra los libros más relevantes usando inteligencia artificial.

## Cómo funciona

1. Las descripciones de los libros (obtenidas de OpenLibrary) se traducen al español con **Ollama Cloud** (`gemma3:12b`)
2. Se generan embeddings vectoriales con **Cloudflare Workers AI** (`bge-m3`, 1024 dims)
3. Los vectores se almacenan en **Supabase** con la extensión `pgvector`
4. Al buscar, la query se traduce y embeddea de la misma forma, y se compara por similitud coseno

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3 + Vite |
| Backend | Python + FastAPI |
| Base de datos | Supabase (PostgreSQL + pgvector) |
| Embeddings | Cloudflare Workers AI (`@cf/baai/bge-m3`) |
| Traducción | Ollama Cloud (`gemma3:12b`) |
| Deploy | Vercel |

## Estructura

```
semantic-search-libros/
├── api/
│   └── index.py              # Entry point para Vercel (monta /api)
├── backend/
│   ├── main.py               # FastAPI: /search, /books, /seed, /csrf-token
│   ├── requirements.txt
│   ├── supabase_setup.sql    # Schema inicial (pgvector, tabla books, función search_books)
│   ├── seed_books.py         # Seed standalone por queries
│   ├── migrate_translations.py  # Traduce descriptions existentes
│   ├── migrate_embeddings.py    # Re-embeddea todos los libros
│   ├── complete_embeddings.py   # Completa embeddings faltantes
│   ├── fix_missing_translations.py  # Traduce + embeddea IDs específicos
│   └── src/
│       ├── config.py         # Variables de entorno
│       ├── embeddings.py     # Cloudflare Workers AI
│       ├── translate.py      # Ollama Cloud
│       ├── openlibrary.py    # Fetch libros desde OpenLibrary API
│       ├── seed.py           # Lógica de carga con traducción + embedding
│       └── csrf.py           # Protección CSRF (double submit cookie)
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── api/search.js
│   │   └── components/
│   │       ├── SearchBar.vue
│   │       ├── BookCard.vue
│   │       └── SeedPanel.vue
│   └── vite.config.js        # Proxy /api → localhost:8000 (solo dev)
├── vercel.json
├── requirements.txt          # Deps Python para Vercel
└── README.md
```

## Setup local

### Prerequisitos

- Python 3.11+
- Node.js 18+
- Cuenta en [Supabase](https://supabase.com)
- Cuenta en [Cloudflare](https://cloudflare.com) (Workers AI)
- Cuenta en [Ollama](https://ollama.com) (cloud API)

### 1. Supabase

Crear un proyecto en Supabase y ejecutar `backend/supabase_setup.sql` en el SQL Editor.

### 2. Variables de entorno

Copiar `backend/.env.example` a `backend/.env` y completar:

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-service-role-key

OLLAMA_CLOUD_URL=https://ollama.com
OLLAMA_API_KEY=your-ollama-api-key
TRANSLATE_MODEL=gemma3:12b

CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-api-token

ALLOWED_ORIGINS=http://localhost:5173
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Cargar libros

```bash
cd backend
source .venv/bin/activate
python seed_books.py --limit 50
```

## Deploy en Vercel

1. Conectar el repositorio en [vercel.com](https://vercel.com)
2. Configurar las variables de entorno en el dashboard (las mismas del `.env` más `ALLOWED_ORIGINS=https://tu-app.vercel.app`)
3. Deploy automático en cada push a `main`

## Seguridad

- **CSRF**: protección via double submit cookie en endpoints que modifican estado (`POST /seed`)
- **CORS**: orígenes permitidos configurados via `ALLOWED_ORIGINS`
- **Service role key**: la clave de Supabase nunca se expone al frontend
