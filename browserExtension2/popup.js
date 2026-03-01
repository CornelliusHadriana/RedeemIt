const fakeCards = [
  {
    id: 1,
    brand: "Amazon",
    category: "Shopping",
    balance: 25.00,
    original_balance: 50.00,
    card_number: "1234567890123456",
    pin: "7890",
    logo_url: "https://logo.clearbit.com/amazon.com",
    last_used: null,
    expiration_date: "2027-06-01"
  },
  {
    id: 2,
    brand: "Target",
    category: "Shopping",
    balance: 15.50,
    original_balance: 25.00,
    card_number: "9876543210987654",
    pin: "1234",
    logo_url: "https://logo.clearbit.com/target.com",
    last_used: null,
    expiration_date: "2026-12-31"
  }
]

document.addEventListener('DOMContentLoaded', () => {
  const cardsList = document.getElementById('cards-list')

  fakeCards.forEach(card => {
    const cardEl = document.createElement('div')
    cardEl.className = 'card'

    cardEl.innerHTML = `
      <div class="card-header">
        <img class="card-logo" src="${card.logo_url}" onerror="this.style.display='none'" />
        <span class="card-brand">${card.brand}</span>
      </div>
      <div class="card-balance">Balance: $${card.balance.toFixed(2)}</div>
      <div class="card-expiry">Expires: ${formatDate(card.expiration_date)}</div>
      <button data-id="${card.id}">Use this card</button>
    `

    cardsList.appendChild(cardEl)

    const button = cardEl.querySelector('button')

    button.addEventListener('click', () => {
      const cardId = parseInt(button.dataset.id)
      const card = fakeCards.find(c => c.id === cardId)

      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'fillCard',
          card: card
        })
      })

      window.close()
    })
  })
})

function formatDate(dateStr) {
  if (!dateStr) return 'No expiration'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}