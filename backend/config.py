from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  data_dir: Path = Path(__file__).resolve().parent / "data"
  database_url: str = "sqlite:///./data/trading.db"
  cors_origins: List[str] = ["http://localhost:5173"]
  default_symbol: str = "AAPL"
  initial_cash: float = 100_000.0
  default_units: int = 10

  class Config:
    env_prefix = "TRADER_"


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
