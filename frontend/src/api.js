import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8006'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 30000,
})

export const stockApi = {
  health: () => api.get('/health'),

  scan: (params = {}) => api.post('/scan', params),
  getScanResults: () => api.get('/scan/results'),
  getScanHistory: () => api.get('/scan/history'),

  getPortfolio: () => api.get('/portfolio'),
  buyStock: (data) => api.post('/portfolio/buy', data),
  sellStock: (data) => api.post('/portfolio/sell', data),

  getQuote: (symbol) => api.get(`/stocks/quote/${symbol}`),

  getWatchlist: () => api.get('/watchlist'),
  addToWatchlist: (symbol) => api.post('/watchlist', { symbol }),

  getAlerts: () => api.get('/alerts'),
  createAlert: (data) => api.post('/alerts', data),
}
