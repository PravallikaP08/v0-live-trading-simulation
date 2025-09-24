from typing import Dict, List, Any
from datetime import datetime
import asyncio
from ..models import Portfolio, Position, Trade
from ..database import get_db
from sqlalchemy.orm import Session


class PortfolioManager:
    def __init__(self, initial_cash: float = 100000.0):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        
    def get_portfolio_summary(self) -> Portfolio:
        """Get current portfolio summary"""
        total_value = self.cash
        total_pnl = 0.0
        
        for symbol, position in self.positions.items():
            position_value = position.quantity * position.current_price
            total_value += position_value
            total_pnl += position.unrealized_pnl
        
        return Portfolio(
            cash=self.cash,
            total_value=total_value,
            total_pnl=total_pnl,
            positions=list(self.positions.values())
        )
    
    def execute_trade(self, symbol: str, action: str, quantity: int, price: float) -> Trade:
        """Execute a trade and update portfolio"""
        trade_value = quantity * price
        
        if action.upper() == "BUY":
            if self.cash >= trade_value:
                self.cash -= trade_value
                
                if symbol in self.positions:
                    # Update existing position
                    pos = self.positions[symbol]
                    new_quantity = pos.quantity + quantity
                    new_avg_price = ((pos.quantity * pos.avg_price) + trade_value) / new_quantity
                    pos.quantity = new_quantity
                    pos.avg_price = new_avg_price
                else:
                    # Create new position
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=quantity,
                        avg_price=price,
                        current_price=price,
                        unrealized_pnl=0.0
                    )
                
                trade = Trade(
                    symbol=symbol,
                    action=action.upper(),
                    quantity=quantity,
                    price=price,
                    timestamp=datetime.now()
                )
                self.trades.append(trade)
                return trade
            else:
                raise ValueError("Insufficient cash for purchase")
                
        elif action.upper() == "SELL":
            if symbol in self.positions and self.positions[symbol].quantity >= quantity:
                self.cash += trade_value
                pos = self.positions[symbol]
                pos.quantity -= quantity
                
                if pos.quantity == 0:
                    del self.positions[symbol]
                
                trade = Trade(
                    symbol=symbol,
                    action=action.upper(),
                    quantity=quantity,
                    price=price,
                    timestamp=datetime.now()
                )
                self.trades.append(trade)
                return trade
            else:
                raise ValueError("Insufficient shares to sell")
        
        raise ValueError(f"Invalid action: {action}")
    
    def update_position_prices(self, price_updates: Dict[str, float]):
        """Update current prices for positions"""
        for symbol, price in price_updates.items():
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.current_price = price
                pos.unrealized_pnl = (price - pos.avg_price) * pos.quantity
    
    def reset(self):
        """Reset portfolio to initial state"""
        self.cash = self.initial_cash
        self.positions = {}
        self.trades = []
