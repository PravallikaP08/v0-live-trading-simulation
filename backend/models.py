from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Trade(Base):
  __tablename__ = "trades"

  id = Column(Integer, primary_key=True, index=True)
  timestamp = Column(DateTime(timezone=True), default=func.now(), index=True)
  symbol = Column(String, index=True)
  side = Column(String(length=4))
  price = Column(Float)
  quantity = Column(Float)
  pnl = Column(Float, default=0.0)
  strategy = Column(String, index=True)


class PortfolioSnapshot(Base):
  __tablename__ = "portfolio_snapshots"

  id = Column(Integer, primary_key=True, index=True)
  timestamp = Column(DateTime(timezone=True), default=func.now(), index=True)
  cash = Column(Float)
  equity = Column(Float)
  position = Column(Float)
  avg_price = Column(Float)
  realized_pnl = Column(Float)
  unrealized_pnl = Column(Float)
