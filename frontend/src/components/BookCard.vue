<script setup>
defineProps({
  book: Object,
  rank: Number,
})

function similarityColor(score) {
  if (score >= 0.85) return '#56cfb2'
  if (score >= 0.70) return '#7c6ff7'
  return '#8888a8'
}

function similarityLabel(score) {
  if (score >= 0.85) return 'Muy relevante'
  if (score >= 0.70) return 'Relevante'
  return 'Relacionado'
}
</script>

<template>
  <article class="card">
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
        <span class="badge" :style="{ color: similarityColor(book.similarity) }">
          {{ similarityLabel(book.similarity) }}
          · {{ (book.similarity * 100).toFixed(1) }}%
        </span>
      </div>

      <h3 class="title">{{ book.title }}</h3>
      <p class="author">{{ book.author }} <span v-if="book.year">· {{ book.year }}</span></p>
      <p class="description">{{ book.description_es || book.description }}</p>
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
}

.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
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
</style>
