import { useState, useEffect } from 'react'
import { Play, Loader2, TrendingUp, TrendingDown, Minus, Brain, Activity, Shield, Target } from 'lucide-react'
import { useStockStore } from '../store'

export default function ScanPage() {
  const {
    scanResults,
    isScanning,
    scanError,
    selectedStocks,
    triggerScan,
    fetchScanResults,
    toggleStockSelection,
    buyStock,
  } = useStockStore()

  const [market, setMarket] = useState('all')
  const [maxStocks, setMaxStocks] = useState(50)

  useEffect(() => {
    fetchScanResults()
  }, [])

  const handleScan = async () => {
    try {
      await triggerScan({ market, max_stocks: maxStocks })
    } catch (error) {
      console.error('Scan failed:', error)
    }
  }

  const handleBuySelected = async () => {
    if (selectedStocks.size === 0) return

    for (const symbol of selectedStocks) {
      const stock = scanResults?.top_picks?.find((s) => s.symbol === symbol)
      if (stock) {
        try {
          await buyStock(symbol, stock.price)
        } catch (error) {
          console.error(`Failed to buy ${symbol}:`, error)
        }
      }
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-radial from-primary-500/10 to-transparent rounded-full blur-3xl" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-primary-500" />
            </div>
            <h1 className="text-2xl font-bold gradient-text">Daily Market Scan</h1>
          </div>
          <p className="text-gray-400 mb-6 max-w-2xl">
            Multi-model ensemble analysis using 17 strategies including LSTM, Transformer,
            candlestick patterns, and technical indicators. Scans 50+ US & Canada stocks.
          </p>

        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Market</label>
            <select
              value={market}
              onChange={(e) => setMarket(e.target.value)}
              className="bg-dark-700 border border-white/10 rounded-lg px-4 py-2 text-white"
            >
              <option value="all">All Markets</option>
              <option value="us">US Only</option>
              <option value="ca">Canada Only</option>
              <option value="tech">Tech Stocks</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Max Stocks</label>
            <input
              type="number"
              value={maxStocks}
              onChange={(e) => setMaxStocks(parseInt(e.target.value))}
              className="bg-dark-700 border border-white/10 rounded-lg px-4 py-2 text-white w-24"
              min={10}
              max={100}
            />
          </div>

          <button
            onClick={handleScan}
            disabled={isScanning}
            className="btn-primary flex items-center gap-2 disabled:opacity-50"
          >
            {isScanning ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                Scanning...
              </>
            ) : (
              <>
                <Play size={18} />
                Run Scan
              </>
            )}
          </button>

          {selectedStocks.size > 0 && (
            <button onClick={handleBuySelected} className="btn-success">
              Buy Selected ({selectedStocks.size})
            </button>
          )}
        </div>

        {scanError && (
          <div className="mt-4 p-4 bg-danger/10 border border-danger/30 rounded-lg text-danger">
            {scanError}
          </div>
        )}
      </div>

      {/* Results */}
      {scanResults?.top_picks && (
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex justify-between items-center mb-2">
            <div>
              <h2 className="text-xl font-bold">Top 5 Picks</h2>
              <p className="text-sm text-gray-400">
                Scanned {scanResults.total_scanned} stocks • {new Date(scanResults.date).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Models Legend */}
          <div className="flex flex-wrap gap-2 mb-6 p-3 bg-white/5 rounded-xl">
            <div className="flex items-center gap-1.5">
              <Brain className="w-3 h-3 text-primary-500" />
              <span className="text-xs text-gray-400">17 Models:</span>
            </div>
            {['LSTM', 'Transformer', 'Patterns', 'Strategies'].map((model, i) => (
              <span key={model} className="text-xs px-2 py-0.5 bg-white/10 rounded text-gray-300">
                {model}
              </span>
            ))}
          </div>

          <div className="grid gap-4">
            {scanResults.top_picks.map((stock, index) => (
              <StockCard
                key={stock.symbol}
                stock={stock}
                rank={index + 1}
                isSelected={selectedStocks.has(stock.symbol)}
                onToggle={() => toggleStockSelection(stock.symbol)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

const ActionIcon = ({ action }) => {
  if (action === 'buy') {
    return <TrendingUp className="text-success" size={16} />
  }
  if (action === 'sell') {
    return <TrendingDown className="text-danger" size={16} />
  }
  return <Minus className="text-warning" size={16} />
}

function StockCard({ stock, rank, isSelected, onToggle }) {

  const getActionClass = (action) => {
    switch (action) {
      case 'buy':
        return 'bg-success/10 border-success text-success'
      case 'sell':
        return 'bg-danger/10 border-danger text-danger'
      default:
        return 'bg-warning/10 border-warning text-warning'
    }
  }

  const getConfidenceColor = (conf) => {
    if (conf >= 80) return 'text-success'
    if (conf >= 60) return 'text-warning'
    return 'text-gray-400'
  }

  return (
    <div
      className={`p-5 rounded-xl border transition-all cursor-pointer ${
        isSelected
          ? 'border-success bg-success/5 shadow-glow-success'
          : 'border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/[0.08]'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-center gap-4">
        {/* Rank */}
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-base ${
            rank === 1
              ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-black'
              : rank === 2
              ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-black'
              : rank === 3
              ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-black'
              : 'bg-white/10 text-gray-400'
          }`}
        >
          #{rank}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-lg font-bold">{stock.symbol}</span>
            <span className="text-sm text-gray-400 truncate max-w-[150px]">{stock.name}</span>
          </div>
          <div className="flex items-center gap-3 mt-1 text-sm flex-wrap">
            <span className="text-white font-semibold text-base">${stock.price?.toFixed(2) || '0.00'}</span>
            <span
              className={`px-1.5 py-0.5 rounded text-xs ${
                stock.change_7d >= 0 ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
              }`}
            >
              {stock.change_7d >= 0 ? '+' : ''}{stock.change_7d?.toFixed(2) || 0}%
            </span>
            <span className="text-gray-500 text-xs">7d</span>
          </div>
        </div>

        {/* Stats */}
        <div className="text-right min-w-[60px]">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Score</div>
          <div className="text-2xl font-bold text-primary-500">
            {stock.score?.toFixed(0) || 0}
          </div>
        </div>

        {/* Confidence */}
        <div className="text-right min-w-[60px]">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Conf</div>
          <div className={`text-xl font-bold ${getConfidenceColor(stock.confidence)}`}>
            {stock.confidence?.toFixed(0) || 0}%
          </div>
        </div>

        {/* Action */}
        <div
          className={`px-4 py-2 rounded-full text-sm font-bold border flex items-center gap-1.5 shadow-lg ${getActionClass(
            stock.action
          )}`}
        >
          <ActionIcon action={stock.action} />
          {stock.action?.toUpperCase() || 'HOLD'}
        </div>

        {/* Checkbox */}
        <div
          className={`w-7 h-7 rounded-lg border-2 flex items-center justify-center transition-colors ${
            isSelected
              ? 'bg-success border-success'
              : 'border-white/30 hover:border-white/50'
          }`}
        >
          {isSelected && <span className="text-black text-xs font-bold">✓</span>}
        </div>
      </div>

      {/* Probabilities Bar */}
      <div className="mt-4 px-1">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden flex shadow-inner">
          <div
            className="bg-success transition-all duration-500"
            style={{ width: `${stock.probabilities?.buy || 0}%` }}
          />
          <div
            className="bg-warning transition-all duration-500"
            style={{ width: `${stock.probabilities?.hold || 0}%` }}
          />
          <div
            className="bg-danger transition-all duration-500"
            style={{ width: `${stock.probabilities?.sell || 0}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span className="text-success font-medium">Buy {stock.probabilities?.buy?.toFixed(1) || 0}%</span>
          <span className="text-warning font-medium">Hold {stock.probabilities?.hold?.toFixed(1) || 0}%</span>
          <span className="text-danger font-medium">Sell {stock.probabilities?.sell?.toFixed(1) || 0}%</span>
        </div>
      </div>
    </div>
  )
}
