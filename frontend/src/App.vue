<script setup>
import { ref, onMounted } from 'vue'
import SearchBar from './components/SearchBar.vue'
import BookCard from './components/BookCard.vue'
import BookList from './components/BookList.vue'
import SeedPanel from './components/SeedPanel.vue'

const loading = ref(false)
const results = ref([])
const lastQuery = ref('')
const hydeDescription = ref('')
const error = ref('')
const showSeed = ref(false)

function setUrlQuery(query) {
  const url = new URL(window.location)
  if (query) {
    url.searchParams.set('q', query)
  } else {
    url.searchParams.delete('q')
  }
  history.pushState({}, '', url)
}

function clearSearch() {
  results.value = []
  lastQuery.value = ''
  hydeDescription.value = ''
  error.value = ''
  setUrlQuery('')
}

async function handleSearch(query) {
  loading.value = true
  error.value = ''
  results.value = []
  hydeDescription.value = ''
  lastQuery.value = query
  setUrlQuery(query)
  try {
    const data = await (await fetch(`/api/search?q=${encodeURIComponent(query)}&top=8`)).json()
    results.value = data.results ?? []
    hydeDescription.value = data.hyde_description ?? ''
  } catch (e) {
    error.value = 'Error al conectar con el servidor.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const q = new URLSearchParams(window.location.search).get('q')
  if (q) handleSearch(q)
})
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <span>Semantic Book Search</span>
        </div>
        <button class="seed-btn" @click="showSeed = !showSeed">
          {{ showSeed ? 'Cerrar' : 'Cargar libros' }}
        </button>
      </div>
    </header>

    <main class="main">
      <transition name="panel">
        <div v-if="showSeed" class="seed-wrap">
          <SeedPanel />
        </div>
      </transition>

      <div class="search-wrap">
        <SearchBar :loading="loading" :initialQuery="lastQuery" @search="handleSearch" @clear="clearSearch" />
      </div>

      <!-- Resultados de búsqueda -->
      <template v-if="lastQuery">
        <div v-if="loading" class="loading-state">
          <div class="pulse" />
          <div class="pulse" style="width:60%;opacity:.6" />
          <div class="pulse" style="width:80%;opacity:.4" />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <section v-if="results.length" class="results">
          <div class="results-header">
            <h2>Resultados para <em>"{{ lastQuery }}"</em></h2>
            <span class="count">{{ results.length }} libros</span>
            <button class="clear-btn" @click="clearSearch">✕ Limpiar</button>
          </div>
          <div v-if="hydeDescription" class="hyde-description">
            <span class="hyde-label">Búsqueda interpretada como</span>
            <p>{{ hydeDescription }}</p>
          </div>
          <div class="results-list">
            <BookCard
              v-for="(book, i) in results"
              :key="book.id"
              :book="book"
              :rank="i + 1"
            />
          </div>
        </section>

        <div v-if="!loading && !results.length" class="empty">
          <p>No se encontraron libros para "{{ lastQuery }}".</p>
          <p class="hint">¿Cargaste libros en la base? Usá el botón "Cargar libros" arriba.</p>
        </div>
      </template>

      <!-- Lista por defecto -->
      <BookList v-else />
    </main>
  </div>
</template>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }

.header {
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(15,15,19,0.85);
}

.header-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1rem;
  color: var(--text);
}

.logo svg { width: 22px; height: 22px; color: var(--accent); }

.seed-btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all var(--transition);
}
.seed-btn:hover { border-color: var(--accent); color: var(--text); }

.main {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
  width: 100%;
}

.seed-wrap { margin-bottom: 32px; }
.panel-enter-active, .panel-leave-active { transition: all 0.25s ease; }
.panel-enter-from, .panel-leave-to { opacity: 0; transform: translateY(-10px); }

.hero {
  text-align: center;
  margin-bottom: 40px;
}

.hero h1 {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 16px;
}

.accent { color: var(--accent); }

.hero p {
  font-size: 1.05rem;
  color: var(--text-muted);
  max-width: 560px;
  margin: 0 auto;
}

.search-wrap { margin-bottom: 48px; }

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.pulse {
  height: 110px;
  background: var(--surface);
  border-radius: var(--radius);
  animation: pulse 1.4s ease-in-out infinite;
  width: 100%;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.error-msg {
  background: rgba(247,112,111,0.1);
  color: var(--danger);
  padding: 14px 18px;
  border-radius: var(--radius);
  font-size: 0.9rem;
}

.results-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
}

.results-header h2 { font-size: 1.1rem; font-weight: 600; }
.results-header em { font-style: normal; color: var(--accent); }
.count { font-size: 0.8rem; color: var(--text-muted); background: var(--surface); padding: 2px 10px; border-radius: 20px; border: 1px solid var(--border); }

.results-list { display: flex; flex-direction: column; gap: 14px; }

.hyde-description {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--surface);
  border-left: 3px solid var(--accent);
  border-radius: 0 var(--radius) var(--radius) 0;
}

.hyde-label {
  display: block;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--accent);
  font-weight: 700;
  margin-bottom: 6px;
}

.hyde-description p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0;
}

.clear-btn {
  margin-left: auto;
  background: none;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: all var(--transition);
}
.clear-btn:hover { border-color: var(--danger); color: var(--danger); }

.empty {
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}
.empty .hint { font-size: 0.85rem; margin-top: 8px; }
</style>
