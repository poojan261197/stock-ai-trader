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

## Multi-Model Prediction System (2026-03-18 Session)

### Analysis Modules Created
- **analysis/patterns.py** - Candlestick pattern detection (doji, hammer, engulfing)
- **analysis/technical_strategies.py** - Multi-strategy analyzer with momentum, mean reversion, breakout, trend following, volume confirmation
- **analysis/trading_strategies.py** - Pattern detection (double top/bottom, breakout signals)
- **market_scanner_enhanced.py** - Multi-model ensemble scanner (NEW)

### ML Models Trained
```
Training Results:
- LSTM: 58.9% accuracy (18,055 training sequences)
- Transformer: 53.5% accuracy
- Label distribution: 51.8% hold, 28% buy, 20.3% sell
- Training set: 25 major stocks across Tech, Finance, Healthcare, Energy, Consumer, ETFs
```

### Ensemble Decision Logic
The scanner combines signals from multiple models:
1. **Pattern Analysis**: Candlestick patterns, chart patterns (double tops/bottoms)
2. **Technical Strategies**: 5 strategies vote (momentum, mean reversion, breakout, trend following, volume confirmation)
3. **LSTM Signal**: Neural network prediction with confidence weight
4. **Transformer Signal**: Transformer model prediction with confidence weight
5. **Trading Cues**: Trend strength, support/resistance proximity, volume spikes

**Voting weights**: Pattern=1, Strategy=1, LSTM/Transformer=0.5 each, Trading cues=0.3-0.5

### Risk Management
- ATR-based stop loss (2x ATR) and take profit (3x ATR)
- Risk-reward ratio calculation for each signal

### Backend Fixed
- Created `backend_api_fixed.py` with proper import handling
- Fixed module structure for analysis packages
- Scanner now returns real predictions

### Scan Results Example
```json
{
  "action": "buy",
  "symbol": "BITO",
  "confidence": 74.07,
  "score": 100,
  "probabilities": {"buy": 56.5, "sell": 43.5, "hold": 0}
}
```

## Incomplete Items

### Not Completed / Partial
- [ ] Configure Wealthsimple OAuth (needs client_id/secret from user)
- [ ] Set up automated daily scanning via cron/systemd
- [ ] Add Redis caching layer for stock prices
- [ ] Implement real price alerts (not just skeleton code)
- [ ] Add authentication/login system
- [ ] Create mobile responsive adjustments
- [ ] Add dark/light theme toggle
- [ ] WebSocket price streaming (SocketIO skeleton exists)
- [ ] Backtesting engine for strategy validation
- [ ] Optimize ensemble weights based on performance

---

## Session Log

### 2026-03-13 - Initial Complete Build
- [x] Created full-stack architecture (Flask + React)
- [x] Built Dashboard with charts (Recharts)
- [x] Built Portfolio page with holdings & P&L
- [x] Built Scan page with stock recommendations
- [x] Added LSTM + Attention model architecture
- [x] Added Transformer model architecture
- [x] Added Ensemble meta-learning architecture
- [x] Created stock universe (230+ stocks/ETFs)
- [x] Integrated Wealthsimple OAuth skeleton
- [x] Fixed CSS styling (Inter font, glass-morphism)
- [x] Added comprehensive tests
- [x] Created Docker configuration
- [x] Committed and pushed to GitHub (main branch)
- [x] Created CLAUDE.md documentation

## Session Log

### 2026-03-18 - Multi-Model Prediction System Completed
- [x] Created analysis/patterns.py for candlestick pattern detection
- [x] Created analysis/technical_strategies.py (5 trading strategies)
- [x] Created analysis/trading_strategies.py (advanced patterns + ATR)
- [x] Trained LSTM model (58.9% accuracy on 18,055 sequences)
- [x] Trained Transformer model (53.5% accuracy)
- [x] Created market_scanner_enhanced.py with multi-model ensemble
- [x] Created backend_api_fixed.py with proper imports
- [x] Fixed import issues (StockEnsemble -> EnsemblePredictor)
- [x] Fixed StrategyResult dataclass access issue
- [x] Tested enhanced scan returning real predictions
- [x] Backend health check passing with enhanced_scanner=true
- [x] Updated CLAUDE.md with session documentation

### 2026-03-13 - Initial Complete Build
- [x] Created full-stack architecture (Flask + React)
- [x] Built Dashboard with charts (Recharts)
- [x] Built Portfolio page with holdings & P&L
- [x] Built Scan page with stock recommendations
- [x] Added LSTM + Attention model architecture
- [x] Added Transformer model architecture
- [x] Added Ensemble meta-learning architecture
- [x] Created stock universe (230+ stocks/ETFs)
- [x] Integrated Wealthsimple OAuth skeleton
- [x] Fixed CSS styling (Inter font, glass-morphism)
- [x] Added comprehensive tests
- [x] Created Docker configuration
- [x] Committed and pushed to GitHub (main branch)
- [x] Created CLAUDE.md documentation

---

**Last Updated:** 2026-03-18
**Version:** 1.1.0 - Multi-Model Ensemble Release
