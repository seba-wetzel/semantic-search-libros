<script setup>
import { ref } from 'vue'

defineProps({
  book: Object,
  rank: Number,
})

const expanded = ref(false)

function similarityColor(score) {
  if (score >= 0.75) return '#56cfb2'
  if (score >= 0.60) return '#7c6ff7'
  return '#8888a8'
}

function similarityLabel(score) {
  if (score >= 0.75) return 'Muy relevante'
  if (score >= 0.60) return 'Relevante'
  return 'Relacionado'
}

function langLabel(code) {
  const map = { eng: 'Inglés', spa: 'Español', fre: 'Francés', ger: 'Alemán', ita: 'Italiano', por: 'Portugués' }
  return map[code] ?? code.toUpperCase()
}
</script>

<template>
  <article class="card" :class="{ expanded }" @click="expanded = !expanded">
    <div class="card-cover">
      <img
        v-if="book.cover_url"
        :src="book.cover_url"
        :alt="book.title"
        loading="lazy"
      />
      <div v-else class="no-cover">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
      </div>
    </div>

    <div class="card-body">
      <div class="card-meta">
        <span class="rank">#{{ rank }}</span>
        <span v-if="book.similarity != null" class="badge" :style="{ color: similarityColor(book.similarity) }">
          {{ similarityLabel(book.similarity) }}
          · {{ (book.similarity * 100).toFixed(1) }}%
        </span>
        <span v-if="book.match_type === 'fulltext'" class="match-tag fulltext">texto exacto</span>
        <span v-else-if="book.match_type === 'hybrid'" class="match-tag hybrid">semántico + texto</span>
        <span class="expand-hint">{{ expanded ? '▲ menos' : '▼ más' }}</span>
      </div>

      <h3 class="title">{{ book.title }}</h3>
      <p class="author">{{ book.author }} <span v-if="book.year">· {{ book.year }}</span></p>

      <!-- Descripción: truncada o completa -->
      <p class="description" :class="{ full: expanded }">
        {{ book.description_es || book.description }}
      </p>

      <!-- Extras: solo cuando está expandido -->
      <transition name="extras">
        <div v-if="expanded && book.extras" class="extras" @click.stop>
          <div class="extras-grid">
            <div v-if="book.extras.pages" class="extra-item">
              <span class="extra-label">Páginas</span>
              <span class="extra-value">{{ book.extras.pages }}</span>
            </div>
            <div v-if="book.extras.rating" class="extra-item">
              <span class="extra-label">Rating</span>
              <span class="extra-value">★ {{ book.extras.rating }} <span class="rating-count">({{ book.extras.rating_count?.toLocaleString() }})</span></span>
            </div>
            <div v-if="book.extras.publishers?.length" class="extra-item">
              <span class="extra-label">Editorial</span>
              <span class="extra-value">{{ book.extras.publishers[0] }}</span>
            </div>
            <div v-if="book.extras.languages?.length" class="extra-item">
              <span class="extra-label">Idiomas</span>
              <span class="extra-value">{{ book.extras.languages.map(langLabel).join(', ') }}</span>
            </div>
          </div>
          <div v-if="book.extras.subjects?.length" class="subjects">
            <span v-for="s in book.extras.subjects" :key="s" class="subject-tag">{{ s }}</span>
          </div>
        </div>
      </transition>
    </div>
  </article>
</template>

<style scoped>
.card {
  display: flex;
  gap: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: border-color var(--transition), transform var(--transition);
  cursor: pointer;
  user-select: none;
}

.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.card.expanded {
  border-color: var(--accent);
}

.card-cover {
  flex-shrink: 0;
  width: 80px;
  height: 110px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--surface2);
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--border);
}

.no-cover svg { width: 32px; height: 32px; }

.card-body { flex: 1; min-width: 0; }

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.rank {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  background: var(--surface2);
  padding: 2px 8px;
  border-radius: 20px;
}

.badge {
  font-size: 0.75rem;
  font-weight: 600;
}

.match-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.02em;
}
.match-tag.fulltext {
  background: rgba(124, 111, 247, 0.12);
  color: #7c6ff7;
  border: 1px solid rgba(124, 111, 247, 0.3);
}
.match-tag.hybrid {
  background: rgba(86, 207, 178, 0.1);
  color: var(--accent);
  border: 1px solid rgba(86, 207, 178, 0.25);
}

.expand-hint {
  margin-left: auto;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.author {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.description {
  font-size: 0.88rem;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description.full {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
}

/* Extras */
.extras {
  margin-top: 16px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}

.extras-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.extra-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.extra-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.extra-value {
  font-size: 0.85rem;
  color: var(--text);
  font-weight: 500;
}

.rating-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 400;
}

.subjects {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.subject-tag {
  font-size: 0.72rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 3px 10px;
  border-radius: 20px;
}

.extras-enter-active { transition: all 0.2s ease; }
.extras-enter-from { opacity: 0; transform: translateY(-6px); }
</style>
