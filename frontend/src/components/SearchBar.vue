<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: Boolean,
})
const emit = defineEmits(['search'])

const query = ref('')

function submit() {
  const q = query.value.trim()
  if (q.length < 2) return
  emit('search', q)
}
</script>

<template>
  <form class="search-bar" @submit.prevent="submit">
    <div class="input-wrap">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input
        v-model="query"
        type="text"
        placeholder="Describí el libro que buscás en lenguaje natural…"
        :disabled="loading"
        autofocus
      />
      <button type="submit" :disabled="loading || query.trim().length < 2">
        <span v-if="!loading">Buscar</span>
        <span v-else class="spinner" />
      </button>
    </div>
    <p class="hint">Ejemplo: "una historia sobre supervivencia en el espacio" · "romance en París siglo XIX"</p>
  </form>
</template>

<style scoped>
.search-bar {
  width: 100%;
  max-width: 760px;
  margin: 0 auto;
}

.input-wrap {
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 6px 6px 6px 16px;
  gap: 8px;
  transition: border-color var(--transition), box-shadow var(--transition);
}

.input-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.icon {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  flex-shrink: 0;
}

input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 1rem;
  padding: 8px 0;
}

input::placeholder { color: var(--text-muted); }
input:disabled { opacity: 0.5; }

button {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 22px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: opacity var(--transition), transform var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 90px;
}

button:hover:not(:disabled) { opacity: 0.85; transform: translateY(-1px); }
button:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin { to { transform: rotate(360deg); } }

.hint {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--text-muted);
  text-align: center;
}
</style>
