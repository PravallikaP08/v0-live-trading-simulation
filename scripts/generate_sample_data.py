import yfinance as yf
import pandas as pd
import sqlite3
from pathlib import Path
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config import settings

def generate_sample_data():
    """Generate sample historical data using yfinance"""
    print("Generating sample market data...")
    
    # Create data directory
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    
    # Symbols to fetch
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    
    # Create database connection
    db_path = settings.data_dir / "trading.db"
    conn = sqlite3.connect(db_path)
    
    # Create market_data table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            UNIQUE(symbol, timestamp)
        )
    """)
    
    for symbol in symbols:
        try:
            print(f"Fetching data for {symbol}...")
            
            # Fetch 1 year of data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y", interval="1d")
            
            if data.empty:
                print(f"No data found for {symbol}")
                continue
            
            # Prepare data for insertion
            data.reset_index(inplace=True)
            data['symbol'] = symbol
            data.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            # Select only needed columns
            data = data[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            # Insert into database
            data.to_sql('market_data', conn, if_exists='append', index=False)
            print(f"Inserted {len(data)} records for {symbol}")
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    conn.close()
    print("Sample data generation completed!")

if __name__ == "__main__":
    generate_sample_data()
