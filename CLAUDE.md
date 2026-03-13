# StockAI - Claude Development Memory

## Project Overview
**Stock Prediction & Trading System** with React frontend, Flask backend, and ML models (LSTM, Transformer, Ensemble).

**Repository:** https://github.com/poojan261197/stock-ai-trader

## Architecture

### Backend (Python)
- **Main API:** `backend_api.py` (port 8006) - Flask + SocketIO
- **Prediction Engine:** `prediction_engine/` - LSTM, Transformer, Ensemble models
- **Market Scanner:** `realtime-agent/market_scanner.py` - Scans 230+ stocks/ETFs
- **Wealthsimple:** `wealthsimple/` - OAuth + Trading API integration
- **Data:** JSON-based persistence in `data/`

### Frontend (React)
- **Framework:** React 18 + Vite + Tailwind CSS
- **State:** Zustand for global state
- **Charts:** Recharts for visualizations
- **UI:** Lucide icons, glass-morphism design

### Docker
- **Dockerfile:** Multi-stage build with Python 3.11 + Node.js 20
- **Compose:** `docker-compose.yml` for local deployment

## Project Structure
```
Stock-Prediction-Models/
├── backend_api.py              # Flask API (port 8006)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build
├── docker-compose.yml          # Local deployment
├── CLAUDE.md                   # This file
│
├── frontend/                   # React app
│   ├── package.json            # Dependencies
│   ├── vite.config.js          # Proxy to backend
│   ├── tailwind.config.js      # Custom colors/shadows
│   ├── index.html              # Entry HTML
│   └── src/
│       ├── main.jsx            # React entry
│       ├── App.jsx             # Router + Navbar
│       ├── index.css           # Global styles (Inter font)
│       ├── store.js            # Zustand store
│       ├── api.js              # API client
│       └── pages/
│           ├── Dashboard.jsx   # Charts + stats
│           ├── PortfolioPage.jsx # Holdings + P&L
│           └── ScanPage.jsx    # Market scanner
│
├── prediction_engine/          # ML models
│   ├── __init__.py
│   ├── lstm_model.py          # LSTM + Attention
│   ├── transformer_model.py    # Transformer
│   └── ensemble.py            # Meta-learning ensemble
│
├── wealthsimple/               # Broker integration
│   ├── auth.py                # OAuth2
│   └── client.py              # Trading API
│
├── data/                       # Universe + persistence
│   └── stock_universe.py      # 230+ stocks/ETFs
│
├── realtime-agent/             # Core trading engine
│   ├── app.py                 # Main API (port 8005)
│   └── market_scanner.py      # Daily picks generator
│
└── tests/                      # Test suite
    ├── test_backend.py
    └── test_frontend.py
```

## Key Technical Decisions

### Why These Technologies?
1. **Flask + SocketIO:** Simple, works well for real-time price updates
2. **Zustand:** Less boilerplate than Redux, perfect for this scale
3. **Recharts:** React-native, works well with dark theme
4. **Tailwind:** Rapid styling, consistent design system
5. **LSTM+Transformer:** Captures temporal patterns in stock data

### Design System
- **Font:** Inter (Google Fonts)
- **Colors:**
  - Primary: `#00d4ff` (cyan)
  - Success: `#00ff88` (green)
  - Danger: `#ff4d4d` (red)
  - Dark bg: `#0a0a1a` to `#1a1a2e`
- **Shadows:** Custom glow effects for cards

### API Endpoints
```
GET /api/health              # Health check
POST /api/scan               # Trigger market scan
GET /api/scan/results        # Latest scan results
GET /api/portfolio           # Get portfolio
POST /api/portfolio/buy      # Buy stock
POST /api/portfolio/sell     # Sell stock
GET /api/stocks/quote/:sym   # Stock quote
```

## Development Workflow

### Local Development
```bash
# Terminal 1: Backend
cd "C:\Users\pooja\OneDrive\Desktop\Stock-Prediction-Models"
python backend_api.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Access: http://localhost:5173
# Backend: http://localhost:8006
```

### Or use PowerShell script
```powershell
powershell -ExecutionPolicy Bypass -File start-all.ps1
```

### Docker Deployment
```bash
# Build and run
docker-compose up --build

# Or production profile
docker-compose --profile production up --build
```

### Running Tests
```bash
pytest tests/ -v
```

## Common Issues & Solutions

### Issue: Backend not starting
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Frontend "npm error ENOENT"
**Solution:** Make sure you're in frontend/ directory
```bash
cd frontend && npm install && npm run dev
```

### Issue: API connection refused
**Solution:** backend_api.py runs on port 8006, check firewall

### Issue: Fonts look "creepy"
**Solution:** Already fixed - using Inter with antialiasing in index.css

### Issue: Merge conflicts on GitHub
**Solution:** Use `--allow-unrelated-histories -Xours` strategy
```bash
git checkout main
git merge master --allow-unrelated-histories -Xours --no-edit
git push origin main
```

## Stock Universe
**Total:** 230+ stocks and ETFs
- US Stocks: 80+ (AAPL, MSFT, TSLA, etc.)
- Canadian Stocks: 60+ (SHOP.TO, TD.TO, etc.)
- US ETFs: 120+ (SPY, ARKK, BITO, etc.)
- Canadian ETFs: 50+ (XIU.TO, ZAG.TO, etc.)

## Completed Features

### UI/UX
- [x] Glass-morphism design system
- [x] Inter font with antialiasing
- [x] Responsive grid layout
- [x] Animations (fade-in, slide-up)

### Charts
- [x] Portfolio performance area chart
- [x] Asset allocation pie chart
- [x] Price history visualization

### ML Models
- [x] LSTM with attention mechanism
- [x] Transformer time-series model
- [x] Ensemble meta-learning
- [x] Technical analysis signals

### Integrations
- [x] yfinance for market data
- [x] Wealthsimple Trade API (OAuth)
- [x] Flask-SocketIO for real-time updates

### Testing
- [x] Backend unit tests
- [x] Frontend component tests
- [x] API endpoint tests

### DevOps
- [x] Dockerfile multi-stage build
- [x] Docker Compose setup
- [x] .gitignore optimization
- [x] GitHub repository

## What NOT To Do (Lessons Learned)

1. **Don't use wrong base branch** - Always push to `main` not `master` for new GitHub repos
2. **Don't forget to cd into frontend** - npm commands fail from wrong directory
3. **Don't install torch on every run** - It's heavy, use requirements.txt
4. **Don't commit node_modules or __pycache__** - Already in .gitignore
5. **Don't run Flask in production with debug=True** - Use production WSGI

## Quick Reference

### Start Everything
```powershell
cd "C:\Users\pooja\OneDrive\Desktop\Stock-Prediction-Models"
start python backend_api.py
cd frontend
start npm run dev
```

### Git Workflow
```bash
git add -A
git commit -m "message"
git push origin main
```

### Emergency Reset
```bash
git reset --hard HEAD
git clean -fd
```

## Future Enhancements (TODO)
- [ ] GraphQL API for efficient queries
- [ ] Redis caching for stock prices
- [ ] PostgreSQL for historical data
- [ ] WebSocket price streaming
- [ ] Backtesting engine
- [ ] Paper trading mode
- [ ] Mobile app (React Native)
- [ ] Crypto support (BTC, ETH)
- [ ] Options trading support

## Contact/Context
- **User:** poojan261197
- **Working Directory:** C:\Users\pooja\OneDrive\Desktop\Stock-Prediction-Models
- **OS:** Windows
- **Shell:** Git Bash

---

**Last Updated:** 2026-03-13
**Version:** 1.0.0 - Initial Release
