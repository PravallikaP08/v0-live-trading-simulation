import sys
import os
import asyncio
import pandas as pd

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.market_data import MarketDataService
from services.backtesting import BacktestEngine

async def run_sample_backtest():
    """Run sample backtests for all strategies"""
    print("Running sample backtests...")
    
    market_service = MarketDataService()
    
    # Test symbols
    symbols = ['AAPL', 'GOOGL']
    strategies = [
        ('sma', {'short_window': 10, 'long_window': 30}),
        ('rsi', {'period': 14, 'oversold': 30, 'overbought': 70}),
        ('bollinger', {'period': 20, 'std_dev': 2})
    ]
    
    results = []
    
    for symbol in symbols:
        print(f"\nTesting {symbol}...")
        
        try:
            # Get historical data
            data = await market_service.get_historical_data(symbol, days=90)
            
            if data.empty:
                print(f"No data available for {symbol}")
                continue
            
            for strategy_name, params in strategies:
                print(f"  Running {strategy_name} strategy...")
                
                engine = BacktestEngine(initial_cash=100000)
                result = engine.run_backtest(data, strategy_name, **params)
                
                results.append({
                    'symbol': symbol,
                    'strategy': strategy_name,
                    'total_return': result.total_return,
                    'max_drawdown': result.max_drawdown,
                    'sharpe_ratio': result.sharpe_ratio,
                    'total_trades': result.total_trades,
                    'winning_trades': result.winning_trades,
                    'win_rate': result.winning_trades / result.total_trades * 100 if result.total_trades > 0 else 0
                })
                
                print(f"    Return: {result.total_return:.2f}%")
                print(f"    Max Drawdown: {result.max_drawdown:.2f}%")
                print(f"    Trades: {result.total_trades}")
                
        except Exception as e:
            print(f"Error testing {symbol}: {e}")
    
    # Save results
    if results:
        df = pd.DataFrame(results)
        output_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'backtest_results.csv')
        df.to_csv(output_path, index=False)
        print(f"\nBacktest results saved to {output_path}")
        print("\nSummary:")
        print(df.to_string(index=False))
    
    print("\nSample backtest completed!")

if __name__ == "__main__":
    asyncio.run(run_sample_backtest())
