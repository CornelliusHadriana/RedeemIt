const BASE = 'http://localhost:8000'

export async function getCards() {
  const res = await fetch(`${BASE}/giftcards/`)
  return res.json()
}

export async function getCard(id) {
  const res = await fetch(`${BASE}/giftcards/${id}`)
  return res.json()
}

export async function addCard(cardData) {
  const res = await fetch(`${BASE}/giftcards/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cardData)
  })
  return res.json()
}

export async function logSpend(cardId, amount) {
  const res = await fetch(`${BASE}/giftcards/${cardId}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gift_card_id: cardId, amount_spent: amount })
  })
  return res.json()
}

export async function getTransactions(cardId) {
  const res = await fetch(`${BASE}/giftcards/${cardId}/transaction`)
  return res.json()
}

export async function getSummary() {
  const res = await fetch(`${BASE}/giftcards/summary`)
  return res.json()
}