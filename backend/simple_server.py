from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime, timedelta
import random

app = FastAPI(title="Simple Algo Trading API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
portfolio = {"cash": 100000, "total_value": 100000, "total_pnl": 0}
trades = []

def generate_mock_data(symbol: str, days: int = 30):
    """Generate mock historical data"""
    data = []
    base_price = 150
    current_time = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):  # Hourly data
        price_change = random.uniform(-2, 2)
        base_price = max(base_price + price_change, 10)
        
        data.append({
            "timestamp": current_time.isoformat() + "Z",
            "open": round(base_price, 2),
            "high": round(base_price + random.uniform(0, 2), 2),
            "low": round(base_price - random.uniform(0, 2), 2),
            "close": round(base_price, 2),
            "volume": random.randint(500000, 2000000)
        })
        current_time += timedelta(hours=1)
    
    return data

@app.get("/")
async def root():
    return {"message": "Simple Algo Trading System API", "status": "running"}

@app.get("/api/historical/{symbol}")
async def get_historical_data(symbol: str, days: int = 30):
    """Get mock historical market data"""
    data = generate_mock_data(symbol, days)
    return {
        "symbol": symbol,
        "data": data
    }

@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio status"""
    return portfolio

@app.get("/api/trades")
async def get_trades():
    """Get trade history"""
    return trades

@app.post("/api/backtest")
async def run_backtest(request: dict):
    """Run mock backtest"""
    return {
        "symbol": request.get("symbol", "AAPL"),
        "strategy": request.get("strategy", "sma"),
        "result": {
            "total_return": round(random.uniform(5, 25), 2),
            "total_trades": random.randint(15, 50),
            "winning_trades": random.randint(8, 30),
            "losing_trades": random.randint(5, 20),
            "max_drawdown": round(random.uniform(-10, -2), 2),
            "sharpe_ratio": round(random.uniform(0.8, 2.5), 2),
            "equity_curve": [100000 + i * random.randint(-1000, 2000) for i in range(30)],
            "trades": [
                {
                    "timestamp": (datetime.now() - timedelta(days=i)).isoformat() + "Z",
                    "action": "buy" if i % 2 == 0 else "sell",
                    "quantity": random.randint(50, 200),
                    "price": round(150 + random.uniform(-10, 10), 2),
                    "pnl": round(random.uniform(-500, 1000), 2)
                } for i in range(10)
            ]
        }
    }

@app.post("/api/portfolio/reset")
async def reset_portfolio():
    """Reset portfolio to initial state"""
    global portfolio, trades
    portfolio = {"cash": 100000, "total_value": 100000, "total_pnl": 0}
    trades = []
    return {"message": "Portfolio reset successfully"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Simple Trading API Server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
