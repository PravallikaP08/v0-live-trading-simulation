# Quick Start Guide

## Option 1: Run with Simple Backend (Recommended for Testing)

This option runs a simplified backend that doesn't require complex dependencies.

### 1. Start Simple Backend
\`\`\`bash
cd backend
python simple_server.py
\`\`\`

### 2. Start Frontend (in new terminal)
\`\`\`bash
npm install
npm run dev
\`\`\`

### 3. Open Browser
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Option 2: Run with Full Backend

### 1. Install Python Dependencies
\`\`\`bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

# Install minimal dependencies first
pip install fastapi uvicorn sqlalchemy pydantic websockets python-multipart

# Then try data dependencies
pip install numpy pandas yfinance
\`\`\`

### 2. Start Full Backend
\`\`\`bash
python main.py
\`\`\`

### 3. Start Frontend
\`\`\`bash
cd ..
npm install
npm run dev
\`\`\`

## Troubleshooting

- **"Failed to fetch" errors**: The frontend now works in mock mode when backend is unavailable
- **Dependency issues**: Use Option 1 (Simple Backend) to test the system first
- **Port conflicts**: The system will suggest alternative ports if 3000 or 8000 are busy

## Features Available in Mock Mode

- ✅ Real-time price charts with mock data
- ✅ Portfolio tracking
- ✅ Trading simulation
- ✅ Backtest results (mock)
- ✅ All UI components and interactions
- ❌ Real market data (uses generated data)
- ❌ WebSocket streaming (uses local simulation)
