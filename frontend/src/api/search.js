const BASE = '/api'

async function getCsrfToken() {
  const res = await fetch(`${BASE}/csrf-token`, { credentials: 'include' })
  const data = await res.json()
  return data.csrf_token
}

export async function searchBooks(query, top = 5) {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(query)}&top=${top}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Error ${res.status}`)
  }
  return res.json()
}

export async function listBooks({ limit = 20, offset = 0, sortBy = 'created_at', order = 'desc' } = {}) {
  const params = new URLSearchParams({ limit, offset, sort_by: sortBy, order })
  const res = await fetch(`${BASE}/books?${params}`)
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}

export async function seedBooks(query, limit) {
  const csrfToken = await getCsrfToken()
  const res = await fetch(`${BASE}/seed`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'x-csrf-token': csrfToken,
    },
    body: JSON.stringify({ query, limit }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Error ${res.status}`)
  }
  return res.json()
}

export async function getSeedStatus() {
  const res = await fetch(`${BASE}/seed/status`)
  return res.json()
}
