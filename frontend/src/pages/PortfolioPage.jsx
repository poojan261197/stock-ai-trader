import { useEffect, useMemo } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Package, Wallet, ArrowUpRight, ArrowDownRight, History, PieChart } from 'lucide-react'
import { useStockStore } from '../store'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  PieChart as RePieChart,
  Pie,
  AreaChart,
  Area
} from 'recharts'

export default function PortfolioPage() {
  const { portfolio, isLoadingPortfolio, fetchPortfolio, sellStock } = useStockStore()

  useEffect(() => {
    fetchPortfolio()
    const interval = setInterval(fetchPortfolio, 30000)
    return () => clearInterval(interval)
  }, [])

  const stats = useMemo(() => {
    const totalValue = portfolio?.positions?.reduce(
      (sum, p) => sum + (p.current_price || p.buy_price) * (p.quantity || 1),
      0
    ) || 0

    const totalInvested = portfolio?.positions?.reduce(
      (sum, p) => sum + p.buy_price * (p.quantity || 1),
      0
    ) || 0

    const unrealizedPnL = totalValue - totalInvested
    const unrealizedPnLPct = totalInvested > 0 ? (unrealizedPnL / totalInvested) * 100 : 0
    const totalPortfolioValue = totalValue + (portfolio?.cash || 0)

    return { totalValue, totalInvested, unrealizedPnL, unrealizedPnLPct, totalPortfolioValue }
  }, [portfolio])

  const positionData = useMemo(() => {
    return portfolio?.positions?.map(p => {
      const current = p.current_price || p.buy_price
      const quantity = p.quantity || 1
      const marketValue = current * quantity
      const costBasis = p.buy_price * quantity
      const pnl = marketValue - costBasis
      const pnlPct = (pnl / costBasis) * 100

      return {
        symbol: p.symbol,
        marketValue,
        costBasis,
        pnl,
        pnlPct,
        quantity,
        isProfitable: pnl >= 0
      }
    }).sort((a, b) => b.marketValue - a.marketValue) || []
  }, [portfolio])

  const allocationData = useMemo(() => {
    const sectors = {}
    positionData.forEach(pos => {
      // Simplified sector assignment
      const sector = pos.symbol.includes('TO') ? 'Canadian' : 'US Stocks'
      sectors[sector] = (sectors[sector] || 0) + pos.marketValue
    })

    const data = Object.entries(sectors).map(([name, value]) => ({
      name,
      value,
      color: name === 'Canadian' ? '#ff4d4d' : '#00d4ff'
    }))

    if (portfolio?.cash > 0) {
      data.push({ name: 'Cash', value: portfolio.cash, color: '#00ff88' })
    }

    return data
  }, [positionData, portfolio])

  const performanceData = useMemo(() => {
    if (!portfolio?.history?.length) {
      return Array.from({ length: 7 }, (_, i) => ({
        date: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
        value: 10000 + Math.random() * 500 - 250,
      }))
    }

    const data = []
    let runningValue = 10000

    portfolio.history.forEach((h, i) => {
      const date = new Date(h.date)
      const label = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      if (h.action === 'BUY') runningValue -= h.price * (h.quantity || 1)
      if (h.action === 'SELL') runningValue += h.price * (h.quantity || 1)

      if (i % Math.ceil(portfolio.history.length / 7) === 0) {
        data.push({ date: label, value: runningValue })
      }
    })

    return data.length >= 2 ? data : performanceData
  }, [portfolio])

  const handleSell = async (symbol) => {
    const position = portfolio?.positions?.find((p) => p.symbol === symbol)
    if (!position) return

    try {
      await sellStock(symbol, position.current_price)
    } catch (error) {
      alert('Failed to sell: ' + error.message)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="card">
        <div className="flex items-center gap-3 mb-2">
          <PieChart className="w-7 h-7 text-primary-500" />
          <h1 className="heading-1 gradient-text">My Portfolio</h1>
        </div>
        <p className="text-muted">Track your investments and performance</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          icon={<Wallet className="w-5 h-5 text-primary-500" />}
          label="Cash"
          value={`$${(portfolio?.cash || 10000).toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          subtext="Available to invest"
        />
        <SummaryCard
          icon={<Package className="w-5 h-5 text-success" />}
          label="Invested"
          value={`$${stats.totalInvested.toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          subtext="In positions"
        />
        <SummaryCard
          icon={<DollarSign className="w-5 h-5 text-warning" />}
          label="Market Value"
          value={`$${stats.totalValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          subtext="Current positions"
        />
        <SummaryCard
          icon={stats.unrealizedPnL >= 0 ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
          label="Unrealized P&L"
          value={`${stats.unrealizedPnL >= 0 ? '+' : ''}$${Math.abs(stats.unrealizedPnL).toFixed(2)}`}
          valueClass={stats.unrealizedPnL >= 0 ? 'text-success' : 'text-danger'}
          subtext={`${stats.unrealizedPnL >= 0 ? '+' : ''}${stats.unrealizedPnLPct.toFixed(1)}%`}
          trendPositive={stats.unrealizedPnL >= 0}
        />
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="card">
          <h2 className="heading-2 text-white mb-6">Portfolio Value</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0a0a1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  formatter={(v) => [`$${Number(v).toLocaleString()}`, 'Value']}
                />
                <Area type="monotone" dataKey="value" stroke="#00ff88" strokeWidth={2}
                  fillOpacity={1} fill="url(#portfolioGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Allocation Chart */}
        <div className="card">
          <h2 className="heading-2 text-white mb-6">Asset Allocation</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0a0a1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  formatter={(v, n) => [`$${Number(v).toLocaleString()}`, n]}
                />
              </RePieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-2">
            {allocationData.map((item) => (
              <div key={item.name} className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-small text-gray-400">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Positions */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="heading-2 text-white">Active Positions</h2>
            <p className="text-muted text-small">{positionData.length} positions</p>
          </div>
        </div>

        {isLoadingPortfolio ? (
          <div className="text-center py-12">
            <div className="animate-pulse text-muted">Loading positions...</div>
          </div>
        ) : positionData.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-muted">No active positions</p>
            <p className="text-small text-muted mt-2">Go to Scan page to find stocks to buy</p>
          </div>
        ) : (
          <div className="space-y-3">
            {positionData.map((position) => (
              <PositionRow
                key={position.symbol}
                position={position}
                onSell={() => handleSell(position.symbol)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Transaction History */}
      {portfolio?.history?.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-6">
            <History className="w-5 h-5 text-primary-500" />
            <h2 className="heading-2 text-white">Transaction History</h2>
          </div>
          <div className="space-y-2">
            {portfolio.history.slice(-20).reverse().map((tx, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.05] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className={`badge ${tx.action === 'BUY' ? 'badge-success' : 'badge-danger'}`}>
                    {tx.action}
                  </span>
                  <span className="font-semibold">{tx.symbol}</span>
                  <span className="text-small text-muted">
                    {tx.quantity || 1} shares
                  </span>
                </div>
                <div className="text-right">
                  <div className="font-medium">${tx.price.toFixed(2)}</div>
                  <div className="text-small text-muted">
                    {new Date(tx.date).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function SummaryCard({ icon, label, value, subtext, valueClass, trendPositive }) {
  return (
    <div className="card p-5">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-small text-muted">{label}</span>
      </div>
      <div className={`text-2xl font-bold ${valueClass || 'text-white'}`}>{value}</div>
      {subtext && (
        <div className={`text-small mt-1 flex items-center gap-1 ${trendPositive === undefined ? 'text-muted' : trendPositive ? 'text-success' : 'text-danger'}`}>
          {subtext}
        </div>
      )}
    </div>
  )
}

function PositionRow({ position, onSell }) {
  const { symbol, marketValue, costBasis, pnl, pnlPct, quantity, isProfitable } = position

  return (
    <div className={`p-4 rounded-xl border-l-4 ${isProfitable ? 'border-success bg-success/5' : 'border-danger bg-danger/5'}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-white">{symbol}</span>
            <span className="text-small text-muted">{quantity} shares</span>
          </div>
          <div className="text-small text-muted mt-1">
            Cost: ${costBasis.toFixed(2)} | Current: ${marketValue.toFixed(2)}
          </div>
        </div>

        <div className="text-right">
          <div className={`text-lg font-bold ${isProfitable ? 'text-success' : 'text-danger'}`}>
            {isProfitable ? '+' : ''}${pnl.toFixed(2)}
          </div>
          <div className={`text-small ${isProfitable ? 'text-success' : 'text-danger'}`}>
            {pnlPct.toFixed(1)}%
          </div>
        </div>

        <button onClick={onSell} className="btn-danger ml-4">
          Sell
        </button>
      </div>
    </div>
  )
}
