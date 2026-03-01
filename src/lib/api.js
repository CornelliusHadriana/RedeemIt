const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Get stored token
function getToken() {
  return localStorage.getItem('access_token')
}

// Auth headers helper
function authHeaders() {
  const token = getToken()
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

// Auth functions
export async function signup(email, password) {
  const res = await fetch(`${BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  return res.json()
}

export async function login(email, password) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  const data = await res.json()
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token)
  }
  return data
}

export function logout() {
  localStorage.removeItem('access_token')
}

export function isLoggedIn() {
  return !!getToken()
}

// Gift card functions
export async function getCards() {
  const res = await fetch(`${BASE}/giftcards/`, {
    headers: authHeaders()
  })
  return res.json()
}

export async function getCard(id) {
  const res = await fetch(`${BASE}/giftcards/${id}`, {
    headers: authHeaders()
  })
  return res.json()
}

export async function addCard(cardData) {
  const res = await fetch(`${BASE}/giftcards/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(cardData)
  })
  return res.json()
}

export async function deleteCard(id) {
  const res = await fetch(`${BASE}/giftcards/${id}`, {
    method: 'DELETE',
    headers: authHeaders()
  })
  return res.json()
}

export async function logSpend(cardId, amount) {
  const res = await fetch(`${BASE}/giftcards/${cardId}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ amount_spent: amount })
  })
  return res.json()
}

export async function getTransactions(cardId) {
  const res = await fetch(`${BASE}/giftcards/${cardId}/transactions`, {
    headers: authHeaders()
  })
  return res.json()
}

export async function getSummary() {
  const res = await fetch(`${BASE}/giftcards/summary`, {
    headers: authHeaders()
  })
  return res.json()
}

export async function uploadCardImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE}/giftcards/upload`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData
  })
  return res.json()
}

export async function updateCard(id, cardData) {
  const res = await fetch(`${BASE}/giftcards/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(cardData)
  })
  return res.json()
}

export async function getExpiringCards(days) {
  const res = await fetch(`${BASE}/giftcards/expiring?days=${days}`, {
    headers: authHeaders()
  })
  return res.json()
}

export async function getCurrentUser() {
  const res = await fetch(`${BASE}/users/me`, {
    headers: authHeaders()
  })
  return res.json()
}

export async function updateUser(data) {
  const res = await fetch(`${BASE}/users/me`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data)
  })
  return res.json()
}