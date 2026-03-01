import './CardTile.css'
import { useNavigate } from 'react-router-dom'

const BRAND_COLORS = {
  starbucks: { bg: '#00704A', text: '#fff', accent: '#CBA258' },
  amazon: { bg: '#FF9900', text: '#fff', accent: '#232F3E' },
  hollister: { bg: '#1B3A6B', text: '#fff', accent: '#C4A35A' },
  target: { bg: '#CC0000', text: '#fff', accent: '#fff' },
  apple: { bg: '#1d1d1f', text: '#fff', accent: '#0071e3' },
  nike: { bg: '#111', text: '#fff', accent: '#fff' },
  sephora: { bg: '#E2003B', text: '#fff', accent: '#fff' },
  default: { bg: '#FF6B6B', text: '#fff', accent: '#F4C430' },
}

function getBrandColors(name) {
  const key = name?.toLowerCase().trim()
  return BRAND_COLORS[key] || BRAND_COLORS.default
}

function isExpiringSoon(dateStr) {
  if (!dateStr) return false
  return new Date(dateStr) - new Date() < 7 * 24 * 60 * 60 * 1000
}

export default function CardTile({ card, isActive, onExpand }) {
  const colors = getBrandColors(card.brand)
  const expiring = isExpiringSoon(card.expiration_date)
  const percentLeft = card.original_balance > 0
    ? (card.balance / card.original_balance) * 100
    : 100

  return (
    <div
      className={`card-tile ${isActive ? 'card-active' : ''} ${expiring ? 'card-expiring' : ''}`}
      style={{ '--bg': colors.bg, '--text': colors.text, '--accent': colors.accent }}
      onClick={() => isActive && onExpand && onExpand(card, colors.bg)}
    >
      {expiring && <div className="expiry-badge">⚠ Expiring Soon</div>}

      <div className="card-top">
        <span className="card-retailer">{card.brand}</span>
        <span className="card-chip">💳</span>
      </div>

      <div className="card-middle">
        <span className="card-balance">${parseFloat(card.balance).toFixed(2)}</span>
        <span className="card-balance-label">remaining</span>
      </div>

      <div className="card-bottom">
        <div className="card-progress-bar">
          <div className="card-progress-fill" style={{ width: `${percentLeft}%` }} />
        </div>
        <div className="card-meta">
          <span>of ${parseFloat(card.original_balance).toFixed(2)}</span>
          <span>Exp: {card.expiration_date}</span>
        </div>
      </div>
    </div>
  )
}