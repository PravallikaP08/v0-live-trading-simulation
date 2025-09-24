import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import numpy as np

from ..models import Trade, BacktestResult
from .strategies import SMAStrategy, RSIStrategy, BollingerBandsStrategy


class BacktestEngine:
    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        
    def run_backtest(self, data: pd.DataFrame, strategy_name: str, **strategy_params) -> BacktestResult:
        """Run backtest for given strategy and data"""
        self.reset()
        
        # Initialize strategy
        if strategy_name == "sma":
            strategy = SMAStrategy(**strategy_params)
        elif strategy_name == "rsi":
            strategy = RSIStrategy(**strategy_params)
        elif strategy_name == "bollinger":
            strategy = BollingerBandsStrategy(**strategy_params)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Execute trades based on signals
        for i, row in data.iterrows():
            current_price = row['close']
            signal = signals.loc[i, 'signal'] if i in signals.index else 0
            
            # Execute trade based on signal
            if signal == 1 and self.position <= 0:  # Buy signal
                self._execute_buy(i, current_price, row['timestamp'])
            elif signal == -1 and self.position > 0:  # Sell signal
                self._execute_sell(i, current_price, row['timestamp'])
            
            # Record equity
            current_equity = self.cash + (self.position * current_price)
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'equity': current_equity,
                'cash': self.cash,
                'position_value': self.position * current_price
            })
        
        # Calculate metrics
        return self._calculate_metrics(data)
    
    def _execute_buy(self, index: int, price: float, timestamp: datetime):
        """Execute buy order"""
        shares_to_buy = int(self.cash // price)
        if shares_to_buy > 0:
            cost = shares_to_buy * price
            self.cash -= cost
            self.position += shares_to_buy
            
            self.trades.append({
                'timestamp': timestamp,
                'type': 'BUY',
                'price': price,
                'quantity': shares_to_buy,
                'value': cost
            })
    
    def _execute_sell(self, index: int, price: float, timestamp: datetime):
        """Execute sell order"""
        if self.position > 0:
            proceeds = self.position * price
            self.cash += proceeds
            
            self.trades.append({
                'timestamp': timestamp,
                'type': 'SELL',
                'price': price,
                'quantity': self.position,
                'value': proceeds
            })
            
            self.position = 0
    
    def _calculate_metrics(self, data: pd.DataFrame) -> BacktestResult:
        """Calculate backtest performance metrics"""
        if not self.equity_curve:
            return BacktestResult(
                total_return=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                equity_curve=[],
                trades=[]
            )
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Total return
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - self.initial_cash) / self.initial_cash * 100
        
        # Max drawdown
        rolling_max = equity_df['equity'].expanding().max()
        drawdown = (equity_df['equity'] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (simplified)
        returns = equity_df['equity'].pct_change().dropna()
        if len(returns) > 1 and returns.std() > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = 0.0
        
        # Trade statistics
        total_trades = len(self.trades)
        buy_trades = [t for t in self.trades if t['type'] == 'BUY']
        sell_trades = [t for t in self.trades if t['type'] == 'SELL']
        
        winning_trades = 0
        losing_trades = 0
        
        for i in range(min(len(buy_trades), len(sell_trades))):
            pnl = sell_trades[i]['value'] - buy_trades[i]['value']
            if pnl > 0:
                winning_trades += 1
            else:
                losing_trades += 1
        
        return BacktestResult(
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            equity_curve=self.equity_curve,
            trades=self.trades
        )
    
    def reset(self):
        """Reset backtest state"""
        self.cash = self.initial_cash
        self.position = 0
        self.trades = []
        self.equity_curve = []
