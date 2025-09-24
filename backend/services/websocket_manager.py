import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .market_data import MarketDataService
from .strategies import SMAStrategy, RSIStrategy, BollingerBandsStrategy
from .portfolio import PortfolioManager


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.market_data_service = MarketDataService()
        self.portfolio_manager = PortfolioManager()
        self.strategies = {
            'sma': SMAStrategy(),
            'rsi': RSIStrategy(),
            'bollinger': BollingerBandsStrategy()
        }
        self.is_streaming = False
        self.current_data = pd.DataFrame()
        
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            message_str = json.dumps(message, default=str)
            disconnected = set()
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.add(connection)
            
            # Remove disconnected clients
            self.active_connections -= disconnected
    
    async def start_streaming(self, symbol: str = "AAPL"):
        """Start streaming market data and signals"""
        if self.is_streaming:
            return
            
        self.is_streaming = True
        
        # Load historical data
        historical_data = await self.market_data_service.get_historical_data(symbol)
        self.current_data = historical_data.copy()
        
        # Start streaming loop
        asyncio.create_task(self._streaming_loop(symbol))
        
    async def stop_streaming(self):
        """Stop streaming market data"""
        self.is_streaming = False
        
    async def _streaming_loop(self, symbol: str):
        """Main streaming loop that generates pseudo-live data"""
        while self.is_streaming:
            try:
                # Generate next candle (simulate live data)
                new_candle = self._generate_next_candle()
                
                # Add to current data
                self.current_data = pd.concat([self.current_data, new_candle], ignore_index=True)
                
                # Keep only last 1000 candles for performance
                if len(self.current_data) > 1000:
                    self.current_data = self.current_data.tail(1000).reset_index(drop=True)
                
                # Generate signals from all strategies
                signals = {}
                for strategy_name, strategy in self.strategies.items():
                    try:
                        strategy_signals = strategy.generate_signals(self.current_data)
                        if not strategy_signals.empty:
                            latest_signal = strategy_signals.iloc[-1]['signal']
                            signals[strategy_name] = int(latest_signal)
                    except Exception as e:
                        signals[strategy_name] = 0
                
                # Update portfolio prices
                current_price = float(new_candle.iloc[0]['close'])
                self.portfolio_manager.update_position_prices({symbol: current_price})
                
                # Execute trades based on signals (using SMA strategy for demo)
                sma_signal = signals.get('sma', 0)
                if sma_signal == 1:  # Buy signal
                    try:
                        trade = self.portfolio_manager.execute_trade(symbol, "BUY", 10, current_price)
                        await self.broadcast({
                            'type': 'trade_executed',
                            'trade': {
                                'symbol': trade.symbol,
                                'action': trade.action,
                                'quantity': trade.quantity,
                                'price': trade.price,
                                'timestamp': trade.timestamp.isoformat()
                            }
                        })
                    except Exception as e:
                        pass  # Insufficient funds or other error
                elif sma_signal == -1:  # Sell signal
                    try:
                        trade = self.portfolio_manager.execute_trade(symbol, "SELL", 10, current_price)
                        await self.broadcast({
                            'type': 'trade_executed',
                            'trade': {
                                'symbol': trade.symbol,
                                'action': trade.action,
                                'quantity': trade.quantity,
                                'price': trade.price,
                                'timestamp': trade.timestamp.isoformat()
                            }
                        })
                    except Exception as e:
                        pass  # Insufficient shares or other error
                
                # Broadcast market data and signals
                await self.broadcast({
                    'type': 'market_data',
                    'symbol': symbol,
                    'candle': {
                        'timestamp': new_candle.iloc[0]['timestamp'].isoformat(),
                        'open': float(new_candle.iloc[0]['open']),
                        'high': float(new_candle.iloc[0]['high']),
                        'low': float(new_candle.iloc[0]['low']),
                        'close': float(new_candle.iloc[0]['close']),
                        'volume': int(new_candle.iloc[0]['volume'])
                    },
                    'signals': signals,
                    'portfolio': {
                        'cash': self.portfolio_manager.cash,
                        'total_value': self.portfolio_manager.get_portfolio_summary().total_value,
                        'total_pnl': self.portfolio_manager.get_portfolio_summary().total_pnl
                    }
                })
                
                # Wait for next update (simulate 1-second intervals)
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error in streaming loop: {e}")
                await asyncio.sleep(1)
    
    def _generate_next_candle(self) -> pd.DataFrame:
        """Generate next candle based on last price with some randomness"""
        if self.current_data.empty:
            # Generate initial candle
            base_price = 150.0
        else:
            base_price = self.current_data.iloc[-1]['close']
        
        # Generate random price movement
        change_percent = np.random.normal(0, 0.02)  # 2% volatility
        new_close = base_price * (1 + change_percent)
        
        # Generate OHLC
        high_low_range = abs(change_percent) * base_price * 2
        new_high = max(base_price, new_close) + np.random.uniform(0, high_low_range)
        new_low = min(base_price, new_close) - np.random.uniform(0, high_low_range)
        new_open = base_price + np.random.uniform(-high_low_range/2, high_low_range/2)
        
        # Generate volume
        base_volume = 1000000
        volume_change = np.random.uniform(0.5, 2.0)
        new_volume = int(base_volume * volume_change)
        
        return pd.DataFrame([{
            'timestamp': datetime.now(),
            'open': new_open,
            'high': new_high,
            'low': new_low,
            'close': new_close,
            'volume': new_volume
        }])
