import { useEffect, useMemo } from 'react'
import {
  TrendingUp, Activity, Zap, ArrowRight,
  PieChart, TrendingDown, BarChart3,
  Target, Sparkles, Wallet
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useStockStore } from '../store'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, PieChart as RePieChart, Pie
} from 'recharts'

export default function Dashboard() {
  const { scanResults, portfolio, fetchScanResults, fetchPortfolio } = useStockStore()

  useEffect(() => {
    fetchScanResults()
    fetchPortfolio()
    const interval = setInterval(() => {
      fetchScanResults()
      fetchPortfolio()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const stats = useMemo(() => {
    const totalValue = portfolio?.positions?.reduce(
      (sum, p) => sum + (p.current_price || p.buy_price) * (p.quantity || 1),
      portfolio?.cash || 10000
    ) || 10000

    const totalInvested = portfolio?.history
      ?.filter((h) => h.action === 'BUY')
      ?.reduce((sum, h) => sum + h.price * (h.quantity || 1), 0) || 0

    const realizedPnL = portfolio?.history?.reduce((sum, h) => {
      if (h.action === 'SELL') return sum + (h.pnl || 0)
      return sum
    }, 0) || 0

    const unrealizedPnL = portfolio?.positions?.reduce((sum, p) => {
      const current = p.current_price || p.buy_price
      return sum + ((current - p.buy_price) * (p.quantity || 1))
    }, 0) || 0

    const totalReturn = realizedPnL + unrealizedPnL
    const totalReturnPct = totalInvested > 0 ? (totalReturn / (totalInvested + (portfolio?.cash || 0))) * 100 : 0

    return { totalValue, totalInvested, realizedPnL, unrealizedPnL, totalReturn, totalReturnPct }
  }, [portfolio])

  const portfolioData = useMemo(() => {
    return portfolio?.positions?.map(p => ({
      symbol: p.symbol,
      value: (p.current_price || p.buy_price) * (p.quantity || 1),
      pnl: ((p.current_price || p.buy_price) - p.buy_price) * (p.quantity || 1),
      pnlPct: ((p.current_price || p.buy_price) - p.buy_price) / p.buy_price * 100
    })) || []
  }, [portfolio])

  const performanceData = useMemo(() => {
    return Array.from({ length: 7 }, (_, i) => ({
      date: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
      value: 10000 + Math.random() * 800,
    }))
  }, [])

  const allocationData = useMemo(() => {
    const cash = portfolio?.cash || 10000
    const invested = stats.totalInvested
    return [
      { name: 'Cash', value: cash, color: '#00d4ff' },
      { name: 'Invested', value: Math.max(0, invested), color: '#00ff88' },
    ]
  }, [portfolio, stats])

  const hasScanResults = scanResults?.top_picks?.length > 0
  const hasPositions = portfolio?.positions?.length > 0

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="card relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-radial from-primary-500/10 to-transparent rounded-full blur-3xl" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-8 h-8 text-primary-500" />
            <h1 className="text-4xl font-bold gradient-text">StockAI Dashboard</h1>
          </div>
          <p className="text-gray-400 text-lg max-w-2xl">
            Advanced AI-powered trading using Deep Evolution Strategy, LSTM, and Transformer models.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Activity className="w-5 h-5 text-primary-500" />}
          label="Portfolio Value"
          value={`$${stats.totalValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          trend={stats.totalReturn >= 0 ? '+' : ''}
          trendValue={`${stats.totalReturnPct.toFixed(1)}%`}
          trendPositive={stats.totalReturn >= 0}
        />
        <StatCard
          icon={<Zap className="w-5 h-5 text-success" />}
          label="Stocks Scanned"
          value={scanResults?.total_scanned || 0}
          subtext={scanResults?.date ? new Date(scanResults.date).toLocaleDateString() : 'Not scanned yet'}
        />
        <StatCard
          icon={<PieChart className="w-5 h-5 text-warning" />}
          label="Active Positions"
          value={portfolio?.positions?.length || 0}
          subtext={`$${(stats.totalInvested).toLocaleString('en-US', { maximumFractionDigits: 0 })} invested`}
        />
        <StatCard
          icon={<Target className="w-5 h-5 text-purple-400" />}
          label="Total Return"
          value={`${stats.totalReturn >= 0 ? '+' : ''}$${Math.abs(stats.totalReturn).toFixed(2)}`}
          trend={stats.totalReturn >= 0 ? '+' : '-'}
          trendValue={`${stats.totalReturnPct.toFixed(1)}%`}
          trendPositive={stats.totalReturn >= 0}
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="heading-2 text-white">Portfolio Performance</h2>
              <p className="text-muted text-small">Value over time</p>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12}
                  tickFormatter={(v) => `$${v.toLocaleString()}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0a0a1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  formatter={(v) => [`$${Number(v).toLocaleString()}`, 'Value']}
                />
                <Area type="monotone" dataKey="value" stroke="#00d4ff" strokeWidth={2}
                  fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h2 className="heading-2 text-white mb-2">Asset Allocation</h2>
          <p className="text-muted text-small mb-6">Cash vs Invested</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0a0a1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  formatter={(v) => [`$${Number(v).toLocaleString()}`, '']}
                />
              </RePieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-4">
            {allocationData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-small text-gray-400">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="heading-2 text-white">Today's Top Picks</h2>
              <p className="text-muted text-small">AI-recommended stocks</p>
            </div>
            <Link to="/scan" className="btn-primary text-small">
              View All <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {!hasScanResults ? (
            <div className="text-center py-12">
              <BarChart3 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-muted mb-2">No scan results yet</p>
              <Link to="/scan" className="text-primary-500 hover:text-primary-400">
                Run market scan
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {scanResults.top_picks.slice(0, 5).map((stock, i) => (
                <div
                  key={stock.symbol}
                  className="flex items-center justify-between p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition-colors border border-transparent hover:border-white/10"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm
                      ${i === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                        i === 1 ? 'bg-gray-400/20 text-gray-300' :
                          i === 2 ? 'bg-orange-500/20 text-orange-400' :
                            'bg-white/10 text-gray-400'}`}>
                      {i + 1}
                    </div>
                    <div>
                      <div className="font-semibold">{stock.symbol}</div>
                      <div className="text-small text-muted">{stock.name}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">${stock.price.toFixed(2)}</div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      stock.action === 'buy' ? 'badge-success' :
                        stock.action === 'sell' ? 'badge-danger' : 'badge-warning'
                    }`}>
                      {stock.action.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="heading-2 text-white">Your Holdings</h2>
              <p className="text-muted text-small">Active positions</p>
            </div>
            <Link to="/portfolio" className="btn-primary text-small">
              Manage <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {!hasPositions ? (
            <div className="text-center py-12">
              <Wallet className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-muted mb-2">No positions yet</p>
              <Link to="/scan" className="text-primary-500 hover:text-primary-400">
                Start investing
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {portfolioData.slice(0, 5).map((pos) => {
                const isProfitable = pos.pnl >= 0
                return (
                  <div key={pos.symbol} className="flex items-center justify-between p-4 rounded-xl bg-white/[0.03]">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-10 rounded-full ${isProfitable ? 'bg-success' : 'bg-danger'}`} />
                      <div>
                        <div className="font-semibold">{pos.symbol}</div>
                        <div className="text-small text-muted">
                          ${pos.value.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`font-medium ${isProfitable ? 'text-success' : 'text-danger'}`}>
                        {isProfitable ? '+' : ''}${pos.pnl.toFixed(2)}
                      </div>
                      <div className={`text-small ${isProfitable ? 'text-success' : 'text-danger'}`}>
                        {pos.pnlPct.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="heading-2 text-white mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Link to="/scan" className="btn-primary">
            <Zap className="w-4 h-4" />
            Run Market Scan
          </Link>
          <Link to="/portfolio" className="btn-success">
            <TrendingUp className="w-4 h-4" />
            View Portfolio
          </Link>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, trend, trendValue, trendPositive, subtext }) {
  return (
    <div className="card p-5 hover:shadow-card-hover transition-shadow">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <span className="text-small text-muted">{label}</span>
      </div>
      <div className="text-2xl md:text-3xl font-bold text-white">{value}</div>
      {trend && (
        <div className={`text-small mt-1 flex items-center gap-1 ${trendPositive ? 'text-success' : 'text-danger'}`}>
          {trendPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {trend}{trendValue}
        </div>
      )}
      {subtext && (
        <div className="text-small text-muted mt-1">{subtext}</div>
      )}
    </div>
  )
}
