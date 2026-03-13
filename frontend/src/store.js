import { create } from 'zustand'
import { stockApi } from './api'

export const useStockStore = create((set, get) => ({
  // Scan results
  scanResults: null,
  scanHistory: [],
  isScanning: false,
  scanError: null,

  // Portfolio
  portfolio: null,
  isLoadingPortfolio: false,

  // Selected stocks
  selectedStocks: new Set(),

  // WebSocket
  socket: null,
  isConnected: false,

  // Actions
  setScanResults: (results) => set({ scanResults: results }),

  triggerScan: async (params = {}) => {
    set({ isScanning: true, scanError: null })
    try {
      const { data } = await stockApi.scan(params)
      set({ scanResults: data, isScanning: false })
      return data
    } catch (error) {
      set({ scanError: error.message, isScanning: false })
      throw error
    }
  },

  fetchScanResults: async () => {
    try {
      const { data } = await stockApi.getScanResults()
      set({ scanResults: data })
      return data
    } catch (error) {
      console.error('Failed to fetch scan results:', error)
    }
  },

  fetchScanHistory: async () => {
    try {
      const { data } = await stockApi.getScanHistory()
      set({ scanHistory: data })
      return data
    } catch (error) {
      console.error('Failed to fetch scan history:', error)
    }
  },

  fetchPortfolio: async () => {
    set({ isLoadingPortfolio: true })
    try {
      const { data } = await stockApi.getPortfolio()
      set({ portfolio: data, isLoadingPortfolio: false })
      return data
    } catch (error) {
      set({ isLoadingPortfolio: false })
      console.error('Failed to fetch portfolio:', error)
    }
  },

  buyStock: async (symbol, price, quantity = 1) => {
    try {
      const { data } = await stockApi.buyStock({ symbol, price, quantity })
      set({ portfolio: data.portfolio })
      return data
    } catch (error) {
      console.error('Failed to buy stock:', error)
      throw error
    }
  },

  sellStock: async (symbol, price) => {
    try {
      const { data } = await stockApi.sellStock({ symbol, price })
      set({ portfolio: data.portfolio })
      return data
    } catch (error) {
      console.error('Failed to sell stock:', error)
      throw error
    }
  },

  toggleStockSelection: (symbol) => {
    const { selectedStocks } = get()
    const newSet = new Set(selectedStocks)
    if (newSet.has(symbol)) {
      newSet.delete(symbol)
    } else {
      newSet.add(symbol)
    }
    set({ selectedStocks: newSet })
  },

  clearSelection: () => set({ selectedStocks: new Set() }),

  setSocket: (socket) => set({ socket }),
  setConnected: (isConnected) => set({ isConnected }),

  updatePortfolio: (portfolio) => set({ portfolio }),
}))
