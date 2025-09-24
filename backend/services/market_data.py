from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

from ..config import settings


class MarketDataService:
  _cache: Dict[str, pd.DataFrame] = {}

  @staticmethod
  def _symbol_path(symbol: str) -> Path:
    return settings.data_dir / f"{symbol.upper()}.csv"

  @classmethod
  def available_symbols(cls) -> List[str]:
    files = settings.data_dir.glob("*.csv")
    return sorted(path.stem.upper() for path in files)

  @classmethod
  def load_dataframe(cls, symbol: str) -> pd.DataFrame:
    norm_symbol = symbol.upper()
    if norm_symbol in cls._cache:
      return cls._cache[norm_symbol].copy()

    path = cls._symbol_path(norm_symbol)
    if not path.exists():
      df = cls._download_symbol(norm_symbol)
    else:
      df = pd.read_csv(path, parse_dates=["timestamp"])

    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)
    cls._cache[norm_symbol] = df
    return df.copy()

  @staticmethod
  def _download_symbol(symbol: str) -> pd.DataFrame:
    try:
      import yfinance as yf
    except ImportError as exc:
      raise RuntimeError(
        "yfinance is required to download data; install backend requirements."
      ) from exc

    data = yf.download(symbol, period="6mo", interval="1d")
    if data.empty:
      raise ValueError(f"No data received for symbol {symbol}")

    data = data.reset_index().rename(
      columns={
        "Date": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
      }
    )
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(settings.data_dir / f"{symbol}.csv", index=False)
    return data

  @classmethod
  def slice_dataframe(
    cls,
    symbol: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
  ) -> pd.DataFrame:
    df = cls.load_dataframe(symbol)
    if start:
      df = df.loc[start:]
    if end:
      df = df.loc[:end]
    return df

  @classmethod
  def to_candles(cls, df: pd.DataFrame) -> List[Dict[str, object]]:
    candles: List[Dict[str, object]] = []
    for ts, row in df.iterrows():
      indicators = {
        k: float(row[k])
        for k in row.index
        if k.startswith("indicator_") and pd.notna(row[k])
      }
      candles.append(
        {
          "timestamp": ts.to_pydatetime(),
          "open": float(row["open"]),
          "high": float(row["high"]),
          "low": float(row["low"]),
          "close": float(row["close"]),
          "volume": float(row["volume"]),
          "indicators": indicators,
          "signal": int(row["signal"]) if "signal" in row else 0,
          "signal_reason": row.get("signal_reason", ""),
        }
      )
    return candles

  @classmethod
  def reset_cache(cls) -> None:
    cls._cache.clear()
