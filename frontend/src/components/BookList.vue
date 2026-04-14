<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { listBooks } from '../api/search.js'
import BookCard from './BookCard.vue'

const PAGE_SIZE = 10

const sortBy = ref('created_at')
const order = ref('desc')
const page = ref(1)

const books = ref([])
const total = ref(0)
const loading = ref(false)
const error = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

const sortFields = [
  { value: 'created_at', label: 'Fecha de carga' },
  { value: 'title',      label: 'Título' },
  { value: 'author',     label: 'Autor' },
  { value: 'year',       label: 'Año' },
]

const orderOptions = [
  { value: 'desc', label: 'Descendente' },
  { value: 'asc',  label: 'Ascendente' },
]

async function fetchBooks() {
  loading.value = true
  error.value = ''
  try {
    const data = await listBooks({
      limit: PAGE_SIZE,
      offset: (page.value - 1) * PAGE_SIZE,
      sortBy: sortBy.value,
      order: order.value,
    })
    books.value = data.books ?? []
    total.value = data.total ?? 0
  } catch (e) {
    error.value = 'Error al cargar libros.'
  } finally {
    loading.value = false
  }
}

function onSortChange() {
  page.value = 1
  fetchBooks()
}

watch(page, fetchBooks)

onMounted(fetchBooks)
</script>

<template>
  <section class="book-list">
    <div class="list-header">
      <div class="list-title">
        <h2>Todos los libros</h2>
        <span v-if="!loading" class="count">{{ total }} libros</span>
      </div>

      <div class="controls">
        <div class="control-group">
          <label>Ordenar por</label>
          <select v-model="sortBy" @change="onSortChange">
            <option v-for="f in sortFields" :key="f.value" :value="f.value">{{ f.label }}</option>
          </select>
        </div>
        <div class="control-group">
          <label>Orden</label>
          <select v-model="order" @change="onSortChange">
            <option v-for="o in orderOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="pulse" v-for="n in 4" :key="n" />
    </div>

    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else-if="books.length === 0" class="empty">
      <p>No hay libros cargados todavía.</p>
      <p class="hint">Usá el botón "Cargar libros" para agregar libros a la base.</p>
    </div>

    <template v-else>
      <div class="results-list">
        <BookCard
          v-for="(book, i) in books"
          :key="book.id"
          :book="book"
          :rank="(page - 1) * 10 + i + 1"
        />
      </div>

      <div class="pagination">
        <button @click="page--" :disabled="page === 1" class="page-btn">← Anterior</button>
        <span class="page-info">Página {{ page }} de {{ totalPages }}</span>
        <button @click="page++" :disabled="page >= totalPages" class="page-btn">Siguiente →</button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.book-list { width: 100%; }

.list-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.list-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.list-title h2 { font-size: 1.1rem; font-weight: 700; }

.count {
  font-size: 0.8rem;
  color: var(--text-muted);
  background: var(--surface);
  padding: 2px 10px;
  border-radius: 20px;
  border: 1px solid var(--border);
}

.controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-group label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.control-group select {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 0.85rem;
  padding: 6px 10px;
  outline: none;
  cursor: pointer;
  transition: border-color var(--transition);
  min-width: 130px;
}

.control-group select:focus { border-color: var(--accent); }

.results-list { display: flex; flex-direction: column; gap: 14px; }

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pulse {
  height: 110px;
  background: var(--surface);
  border-radius: var(--radius);
  animation: pulse 1.4s ease-in-out infinite;
  width: 100%;
}
.pulse:nth-child(2) { opacity: .7; }
.pulse:nth-child(3) { opacity: .5; }
.pulse:nth-child(4) { opacity: .3; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.error-msg {
  background: rgba(247,112,111,0.1);
  color: var(--danger);
  padding: 14px 18px;
  border-radius: var(--radius);
  font-size: 0.9rem;
}

.empty {
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}
.empty .hint { font-size: 0.85rem; margin-top: 8px; }

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.page-btn {
  background: var(--surface);
  border: 1.5px solid var(--border);
  color: var(--text);
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: border-color var(--transition), opacity var(--transition);
}
.page-btn:hover:not(:disabled) { border-color: var(--accent); }
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.page-info {
  font-size: 0.85rem;
  color: var(--text-muted);
  min-width: 120px;
  text-align: center;
}
</style>
