import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { TrendingUp, PieChart, Activity, Settings } from 'lucide-react'
import ScanPage from './pages/ScanPage'
import PortfolioPage from './pages/PortfolioPage'
import Dashboard from './pages/Dashboard'

function Navbar() {
  return (
    <nav className="glass-panel border-b border-white/10 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <Link to="/" className="flex items-center gap-2">
          <TrendingUp className="w-8 h-8 text-primary-500" />
          <span className="text-xl font-bold gradient-text">StockAI</span>
        </Link>

        <div className="flex items-center gap-6">
          <NavLink to="/" icon={<Activity size={18} />} label="Dashboard" />
          <NavLink to="/scan" icon={<TrendingUp size={18} />} label="Scan" />
          <NavLink to="/portfolio" icon={<PieChart size={18} />} label="Portfolio" />
        </div>
      </div>
    </nav>
  )
}

function NavLink({ to, icon, label }) {
  return (
    <Link
      to={to}
      className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-white/5"
    >
      {icon}
      <span>{label}</span>
    </Link>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-900">
        <Navbar />
        <main className="max-w-7xl mx-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
          </Routes>
        </main>
        <footer className="text-center py-8 text-gray-500 text-sm">
          Stock Prediction AI • Deep Evolution Strategy • For educational purposes only
        </footer>
      </div>
    </Router>
  )
}

export default App
