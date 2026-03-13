import { useState, useEffect } from 'react'
import { Play, Loader2, TrendingUp, TrendingDown, Minus } from 'lucide-react'
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
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6">
        <h1 className="text-2xl font-bold mb-4">Daily Market Scan</h1>
        <p className="text-gray-400 mb-6">
          Scan 50+ US and Canada stocks to get AI-powered buy/hold/sell recommendations
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
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-bold">Top 5 Picks</h2>
              <p className="text-sm text-gray-400">
                Scanned {scanResults.total_scanned} stocks on{' '}
                {new Date(scanResults.date).toLocaleDateString()}
              </p>
            </div>
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

function StockCard({ stock, rank, isSelected, onToggle }) {
  const getActionIcon = (action) => {
    switch (action) {
      case 'buy':
        return <TrendingUp className="text-success" size={16} />
      case 'sell':
        return <TrendingDown className="text-danger" size={16} />
      default:
        return <Minus className="text-warning" size={16} />
    }
  }

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

  return (
    <div
      className={`p-4 rounded-xl border transition-all cursor-pointer ${
        isSelected
          ? 'border-success bg-success/5'
          : 'border-white/10 hover:border-white/20 bg-white/5'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-center gap-4">
        {/* Rank */}
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${
            rank === 1
              ? 'bg-yellow-500/20 text-yellow-400'
              : rank === 2
              ? 'bg-gray-400/20 text-gray-300'
              : rank === 3
              ? 'bg-orange-600/20 text-orange-400'
              : 'bg-white/10 text-gray-400'
          }`}
        >
          #{rank}
        </div>

        {/* Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold">{stock.symbol}</span>
            <span className="text-sm text-gray-400">{stock.name}</span>
          </div>
          <div className="flex items-center gap-4 mt-1 text-sm">
            <span className="text-white font-medium">${stock.price.toFixed(2)}</span>
            <span
              className={
                stock.change_7d >= 0 ? 'text-success' : 'text-danger'
              }
            >
              {stock.change_7d >= 0 ? '+' : ''}
              {stock.change_7d.toFixed(2)}% (7d)
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="text-right">
          <div className="text-sm text-gray-400">Score</div>
          <div className="text-lg font-bold text-primary-500">
            {stock.score}
          </div>
        </div>

        {/* Action */}
        <div
          className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center gap-1 ${getActionClass(
            stock.action
          )}`}
        >
          {getActionIcon(stock.action)}
          {stock.action.toUpperCase()}
        </div>

        {/* Checkbox */}
        <div
          className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
            isSelected
              ? 'bg-success border-success'
              : 'border-white/30'
          }`}
        >
          {isSelected && <span className="text-black text-xs">✓</span>}
        </div>
      </div>

      {/* Probabilities */}
      <div className="mt-3 flex gap-2">
        <div className="flex-1">
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden flex">
            <div
              className="bg-success"
              style={{ width: `${stock.probabilities.buy}%` }}
            />
            <div
              className="bg-warning"
              style={{ width: `${stock.probabilities.hold}%` }}
            />
            <div
              className="bg-danger"
              style={{ width: `${stock.probabilities.sell}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span className="text-success">Buy {stock.probabilities.buy}%</span>
            <span className="text-warning">Hold {stock.probabilities.hold}%</span>
            <span className="text-danger">Sell {stock.probabilities.sell}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}
