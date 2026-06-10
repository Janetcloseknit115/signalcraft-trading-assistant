import logging
from dataclasses import dataclass
from typing import List

# Setup global logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@dataclass
class SafetyLimits:
    """Hardcoded safety guardrails for the trading engine."""
    max_position_size_pct: float = 0.02  # Maximum 2% of total portfolio per trade
    max_daily_loss_usd: float = 150.0    # Daily loss limit kill-switch
    max_leverage: int = 1                # Spot only by default
    allowed_assets: tuple = ("BTC/USDT", "ETH/USDT", "SOL/USDT")

@dataclass
class AppConfig:
    """Application-wide configuration state."""
    deepseek_api_key: str
    exchange_id: str
    exchange_api_key: str
    exchange_secret: str
    execution_mode_enabled: bool = False
    paper_trading_mode: bool = True
    user_thesis: str = "I am looking for volume breakouts on major support levels."
