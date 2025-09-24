from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Type

import numpy as np
import pandas as pd


@dataclass
class StrategyDefinition:
  name: str
  label: str
  default_parameters: Dict[str, float]
  overlays: List[str]


class StrategyBase:
  name: str = "base"
  label: str = "Base Strategy"
  default_parameters: Dict[str, float] = {}
  overlays: List[str] = []

  def __init__(self, params: Dict[str, float] | None = None):
    self.params = {**self.default_parameters, **(params or {})}

  def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError

  @staticmethod
  def build_signal_payload(value: int, reason: str) -> Dict[str, str] | None:
    if value == 1:
      return {"type": "BUY", "reason": reason}
    if value == -1:
      return {"type": "SELL", "reason": reason}
    return None

  def extract_signal(self, row: pd.Series) -> Dict[str, str] | None:
    signal_value = int(row.get("signal", 0))
    return self.build_signal_payload(signal_value, row.get("signal_reason", ""))


class SmaEmaStrategy(StrategyBase):
  name = "sma_ema"
  label = "SMA / EMA Crossover"
  default_parameters = {"short_window": 10, "long_window": 30}
  overlays = ["indicator_sma", "indicator_ema"]

  def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    short_window = int(self.params["short_window"])
    long_window = int(self.params["long_window"])
    data["indicator_sma"] = data["close"].rolling(short_window).mean()
    data["indicator_ema"] = data["close"].ewm(span=long_window, adjust=False).mean()

    data["signal"] = 0
    buy_mask = (
      (data["indicator_sma"] >= data["indicator_ema"])
      & (data["indicator_sma"].shift(1) < data["indicator_ema"].shift(1))
    )
    sell_mask = (
      (data["indicator_sma"] <= data["indicator_ema"])
      & (data["indicator_sma"].shift(1) > data["indicator_ema"].shift(1))
    )

    data.loc[buy_mask, "signal"] = 1
    data.loc[sell_mask, "signal"] = -1
    data["signal_reason"] = ""
    data.loc[buy_mask, "signal_reason"] = "SMA crossed above EMA"
    data.loc[sell_mask, "signal_reason"] = "SMA crossed below EMA"
    return data


class RsiMomentumStrategy(StrategyBase):
  name = "rsi_momentum"
  label = "RSI Momentum"
  default_parameters = {"period": 14, "oversold": 30, "overbought": 70}
  overlays = ["indicator_rsi"]

  def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    period = int(self.params["period"])
    oversold = float(self.params["oversold"])
    overbought = float(self.params["overbought"])

    delta = data["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    avg_loss = avg_loss.replace(0, np.nan)

    rs = avg_gain / avg_loss
    data["indicator_rsi"] = 100 - (100 / (1 + rs))
    data["indicator_rsi"] = data["indicator_rsi"].fillna(method="ffill")

    data["signal"] = 0
    buy_mask = (
      (data["indicator_rsi"] >= oversold)
      & (data["indicator_rsi"].shift(1) < oversold)
    )
    sell_mask = (
      (data["indicator_rsi"] <= overbought)
      & (data["indicator_rsi"].shift(1) > overbought)
    )

    data.loc[buy_mask, "signal"] = 1
    data.loc[sell_mask, "signal"] = -1
    data["signal_reason"] = ""
    data.loc[buy_mask, "signal_reason"] = "RSI exited oversold zone"
    data.loc[sell_mask, "signal_reason"] = "RSI exited overbought zone"
    return data


class StrategyFactory:
  _registry: Dict[str, Type[StrategyBase]] = {
    SmaEmaStrategy.name: SmaEmaStrategy,
    RsiMomentumStrategy.name: RsiMomentumStrategy,
  }

  @classmethod
  def create(cls, name: str, params: Dict[str, float] | None = None) -> StrategyBase:
    try:
      strategy_cls = cls._registry[name]
    except KeyError as exc:
      raise ValueError(f"Unknown strategy: {name}") from exc
    return strategy_cls(params)

  @classmethod
  def catalog(cls) -> List[StrategyDefinition]:
    items: List[StrategyDefinition] = []
    for name, strategy_cls in cls._registry.items():
      items.append(
        StrategyDefinition(
          name=name,
          label=strategy_cls.label,
          default_parameters=strategy_cls.default_parameters.copy(),
          overlays=strategy_cls.overlays[:],
        )
      )
    return items
