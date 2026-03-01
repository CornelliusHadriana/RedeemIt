/* global getToken, clearToken, login, signup, getCards, getCard */

// DOM Elements
let cardsList;
let loginForm;
let signupForm;
let logoutBtn;
let errorMessage;
let successMessage;
let loadingSpinner;

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize DOM references
  cardsList = document.getElementById('cards-list');
  loginForm = document.getElementById('login-form');
  signupForm = document.getElementById('signup-form');
  logoutBtn = document.getElementById('logout-btn');
  errorMessage = document.getElementById('error-message');
  successMessage = document.getElementById('success-message');
  loadingSpinner = document.getElementById('loading-spinner');

  // Set up event listeners
  setupEventListeners();

  // Check if user is logged in
  try {
    const token = await getToken();
    if (token) {
      await loadAndRenderCards();
    } else {
      showLoginForm();
    }
  } catch (error) {
    showError(error.message);
    showLoginForm();
  }
});

function setupEventListeners() {
  // Login form submit
  document.getElementById('login-btn').addEventListener('click', handleLogin);
  document.getElementById('login-password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleLogin();
  });

  // Signup form submit
  document.getElementById('signup-btn').addEventListener('click', handleSignup);
  document.getElementById('signup-password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSignup();
  });

  // Toggle between login and signup
  document.getElementById('show-signup').addEventListener('click', () => {
    hideError();
    hideSuccess();
    loginForm.classList.remove('active');
    signupForm.classList.add('active');
  });

  document.getElementById('show-login').addEventListener('click', () => {
    hideError();
    hideSuccess();
    signupForm.classList.remove('active');
    loginForm.classList.add('active');
  });

  // Logout
  logoutBtn.addEventListener('click', handleLogout);
}

async function handleLogin() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!email || !password) {
    showError('Please enter email and password.');
    return;
  }

  hideError();
  hideSuccess();
  showLoading();

  try {
    await login(email, password);
    hideLoading();
    loginForm.classList.remove('active');
    await loadAndRenderCards();
  } catch (error) {
    hideLoading();
    showError(error.message);
  }
}

async function handleSignup() {
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;

  if (!email || !password) {
    showError('Please enter email and password.');
    return;
  }

  if (password.length < 6) {
    showError('Password must be at least 6 characters.');
    return;
  }

  hideError();
  hideSuccess();
  showLoading();

  try {
    await signup(email, password);
    hideLoading();
    showSuccess('Account created! Please log in.');
    signupForm.classList.remove('active');
    loginForm.classList.add('active');
    // Clear signup form
    document.getElementById('signup-email').value = '';
    document.getElementById('signup-password').value = '';
  } catch (error) {
    hideLoading();
    showError(error.message);
  }
}

async function handleLogout() {
  await clearToken();
  cardsList.innerHTML = '';
  logoutBtn.classList.add('hidden');
  showLoginForm();
}

async function loadAndRenderCards() {
  showLoading();
  hideError();

  try {
    const cards = await getCards();
    hideLoading();
    renderCards(cards);
    logoutBtn.classList.remove('hidden');
  } catch (error) {
    hideLoading();
    if (error.message.includes('Session expired') || error.message.includes('Not authenticated')) {
      showLoginForm();
    }
    showError(error.message);
  }
}

function renderCards(cards) {
  cardsList.innerHTML = '';

  if (!cards || cards.length === 0) {
    cardsList.innerHTML = '<div class="empty-state">No gift cards yet. Add some from the web app!</div>';
    return;
  }

  cards.forEach(card => {
    const cardEl = document.createElement('div');
    cardEl.className = 'card';

    const logoUrl = card.logo_url || `https://logo.clearbit.com/${card.brand.toLowerCase().replace(/\s+/g, '')}.com`;
    const balance = card.balance != null ? card.balance.toFixed(2) : '0.00';

    cardEl.innerHTML = `
      <div class="card-header">
        <img class="card-logo" src="${logoUrl}" onerror="this.style.display='none'" />
        <span class="card-brand">${escapeHtml(card.brand)}</span>
      </div>
      <div class="card-balance">Balance: $${balance}</div>
      <div class="card-expiry">Expires: ${formatDate(card.expiration_date)}</div>
      <button data-id="${card.id}">Use this card</button>
    `;

    cardsList.appendChild(cardEl);

    const button = cardEl.querySelector('button');
    button.addEventListener('click', () => handleUseCard(card.id, button));
  });
}

async function handleUseCard(cardId, button) {
  button.disabled = true;
  button.textContent = 'Loading...';

  try {
    const cardDetails = await getCard(cardId);

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'fillCard',
          card: {
            card_number: cardDetails.card_number,
            pin: cardDetails.pin
          }
        });
      }
    });

    window.close();
  } catch (error) {
    button.disabled = false;
    button.textContent = 'Use this card';
    
    if (error.message.includes('Session expired') || error.message.includes('Not authenticated')) {
      showLoginForm();
    }
    showError(error.message);
  }
}

function showLoginForm() {
  loginForm.classList.add('active');
  signupForm.classList.remove('active');
  logoutBtn.classList.add('hidden');
  cardsList.innerHTML = '';
}

function showLoading() {
  loadingSpinner.classList.add('active');
}

function hideLoading() {
  loadingSpinner.classList.remove('active');
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.add('active');
}

function hideError() {
  errorMessage.textContent = '';
  errorMessage.classList.remove('active');
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.classList.add('active');
}

function hideSuccess() {
  successMessage.textContent = '';
  successMessage.classList.remove('active');
}

function formatDate(dateStr) {
  if (!dateStr) return 'No expiration';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}