<script setup>
import { ref, onUnmounted } from 'vue'
import { seedBooks, getSeedStatus } from '../api/search.js'

const query = ref('classic literature')
const limit = ref(20)
const loading = ref(false)
const message = ref('')
const error = ref('')
const status = ref(null)
let pollInterval = null

async function startSeed() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await seedBooks(query.value, limit.value)
    message.value = res.message
    pollStatus()
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
}

function pollStatus() {
  pollInterval = setInterval(async () => {
    const s = await getSeedStatus()
    status.value = s
    if (!s.running) {
      clearInterval(pollInterval)
      loading.value = false
      if (s.last_result) {
        message.value = `✔ Insertados: ${s.last_result.inserted} · Saltados: ${s.last_result.skipped}`
      }
    }
  }, 2000)
}

onUnmounted(() => clearInterval(pollInterval))
</script>

<template>
  <div class="seed-panel">
    <h3>Cargar libros</h3>
    <p class="desc">Buscá libros en OpenLibrary, generá sus embeddings y guardalos en Supabase.</p>

    <div class="fields">
      <div class="field">
        <label>Búsqueda en OpenLibrary</label>
        <input v-model="query" type="text" placeholder="science fiction, classic literature…" :disabled="loading" />
      </div>
      <div class="field field-sm">
        <label>Límite</label>
        <input v-model.number="limit" type="number" min="5" max="100" :disabled="loading" />
      </div>
    </div>

    <button @click="startSeed" :disabled="loading">
      <span v-if="loading">
        <span class="spinner" /> Procesando…
      </span>
      <span v-else>Iniciar seed</span>
    </button>

    <p v-if="message" class="msg success">{{ message }}</p>
    <p v-if="error" class="msg error">{{ error }}</p>

    <div v-if="status?.running" class="running">
      <span class="spinner dark" /> Generando embeddings en background…
    </div>
  </div>
</template>

<style scoped>
.seed-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
}

h3 { font-size: 1rem; font-weight: 700; margin-bottom: 6px; }
.desc { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 18px; }

.fields { display: flex; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.field { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 180px; }
.field-sm { flex: 0 0 100px; min-width: 80px; }

label { font-size: 0.78rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }

input {
  background: var(--surface2);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
  transition: border-color var(--transition);
}
input:focus { border-color: var(--accent); }
input:disabled { opacity: 0.4; }

button {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity var(--transition);
}
button:hover:not(:disabled) { opacity: 0.85; }
button:disabled { opacity: 0.4; cursor: not-allowed; }

.msg { margin-top: 12px; font-size: 0.88rem; padding: 10px 14px; border-radius: 8px; }
.success { background: rgba(86, 207, 178, 0.1); color: var(--accent2); }
.error { background: rgba(247, 112, 111, 0.1); color: var(--danger); }

.running { display: flex; align-items: center; gap: 8px; margin-top: 12px; font-size: 0.85rem; color: var(--text-muted); }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
.spinner.dark {
  border-color: var(--border);
  border-top-color: var(--accent);
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
