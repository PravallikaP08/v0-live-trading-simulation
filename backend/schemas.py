from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Candle(BaseModel):
  timestamp: datetime
  open: float
  high: float
  low: float
  close: float
  volume: float
  indicators: Dict[str, Optional[float]] = Field(default_factory=dict)


class HistoricalResponse(BaseModel):
  symbol: str
  candles: List[Candle]


class StrategyInfo(BaseModel):
  name: str
  label: str
  defaultParameters: Dict[str, float]
  overlays: List[str]


class TradeRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  timestamp: datetime
  symbol: str
  side: str
  price: float
  quantity: float
  pnl: float
  strategy: str


class PortfolioRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  timestamp: datetime
  cash: float
  equity: float
  position: float
  avg_price: float
  realized_pnl: float
  unrealized_pnl: float


class BacktestRequest(BaseModel):
  symbol: str
  strategy: str
  start: Optional[date] = None
  end: Optional[date] = None
  initial_cash: float = 100_000
  units: int = 10
  parameters: Dict[str, float] = Field(default_factory=dict)


class BacktestMetrics(BaseModel):
  total_return_pct: float
  annualized_return_pct: float
  max_drawdown_pct: float
  win_rate_pct: float
  trades_executed: int
  final_equity: float


class BacktestResponse(BaseModel):
  symbol: str
  strategy: str
  metrics: BacktestMetrics
  equity_curve: List[Dict[str, float]]
  trades: List[Dict[str, object]]
