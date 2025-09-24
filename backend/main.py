from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
from typing import List, Optional

from .config import settings
from .database import engine, get_db, Base
from .schemas import *
from .services.market_data import MarketDataService
from .services.backtesting import BacktestEngine
from .services.websocket_manager import WebSocketManager
from .services.portfolio import PortfolioManager

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Algo Trading System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
market_data_service = MarketDataService()
websocket_manager = WebSocketManager()
portfolio_manager = PortfolioManager()

@app.get("/")
async def root():
    return {"message": "Algo Trading System API"}

@app.get("/api/historical/{symbol}", response_model=HistoricalDataResponse)
async def get_historical_data(symbol: str, days: int = 30):
    """Get historical market data for a symbol"""
    try:
        data = await market_data_service.get_historical_data(symbol, days)
        return HistoricalDataResponse(
            symbol=symbol,
            data=[
                CandleData(
                    timestamp=row['timestamp'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume']
                ) for _, row in data.iterrows()
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """Run backtest for a strategy"""
    try:
        # Get historical data
        data = await market_data_service.get_historical_data(request.symbol, request.days)
        
        # Run backtest
        engine = BacktestEngine(request.initial_cash)
        result = engine.run_backtest(
            data, 
            request.strategy,
            **request.strategy_params
        )
        
        return BacktestResponse(
            symbol=request.symbol,
            strategy=request.strategy,
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio", response_model=Portfolio)
async def get_portfolio():
    """Get current portfolio status"""
    return portfolio_manager.get_portfolio_summary()

@app.post("/api/trade", response_model=TradeResponse)
async def execute_trade(request: TradeRequest):
    """Execute a manual trade"""
    try:
        trade = portfolio_manager.execute_trade(
            request.symbol,
            request.action,
            request.quantity,
            request.price
        )
        return TradeResponse(
            success=True,
            trade=trade,
            message="Trade executed successfully"
        )
    except Exception as e:
        return TradeResponse(
            success=False,
            trade=None,
            message=str(e)
        )

@app.get("/api/trades", response_model=List[Trade])
async def get_trades():
    """Get trade history"""
    return portfolio_manager.trades

@app.post("/api/portfolio/reset")
async def reset_portfolio():
    """Reset portfolio to initial state"""
    portfolio_manager.reset()
    return {"message": "Portfolio reset successfully"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = eval(data)  # In production, use json.loads with proper validation
            
            if message.get('action') == 'start_streaming':
                symbol = message.get('symbol', 'AAPL')
                await websocket_manager.start_streaming(symbol)
            elif message.get('action') == 'stop_streaming':
                await websocket_manager.stop_streaming()
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
