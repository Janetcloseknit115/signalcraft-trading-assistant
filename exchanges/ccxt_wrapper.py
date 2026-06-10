import ccxt.async_support as ccxt
import logging
import random
from typing import Dict, Any

logger = logging.getLogger("Exchange")

class ExchangeWrapper:
    """
    Standardized interface for interacting with crypto exchanges via CCXT.
    """
    def __init__(self, exchange_id: str, api_key: str, secret: str, is_paper: bool):
        self.is_paper = is_paper
        self.exchange_class = getattr(ccxt, exchange_id)
        self.client = self.exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        logger.info(f"Connected to {exchange_id.upper()}. Paper Trading: {self.is_paper}")

    async def fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetches latest ticker data. Mocks volume spikes for demonstration."""
        try:
            # In production: await self.client.fetch_ticker(symbol)
            # MOCK DATA FOR DEMO PURPOSES:
            mock_price = random.uniform(50000, 70000) if "BTC" in symbol else random.uniform(2000, 4000)
            mock_volume_spike = random.random() > 0.8 # 20% chance to trigger AI
            
            return {
                "symbol": symbol,
                "price": round(mock_price, 2),
                "volume_spike": mock_volume_spike,
                "timestamp": self.client.milliseconds()
            }
        except Exception as e:
            logger.error(f"Failed to fetch market data for {symbol}: {e}")
            return {}

    async def get_portfolio_balance_usd(self) -> float:
        """Retrieves total portfolio value in USD."""
        # In production: await self.client.fetch_balance()
        return 25000.0  # Mock 25k USD balance

    async def place_market_order(self, action: str, symbol: str, amount: float):
        """Executes a trade or logs it if in paper trading mode."""
        if self.is_paper:
            logger.info(f"📝 [PAPER TRADE] -> Executed {action.upper()} | {amount:.4f} {symbol}")
            return True
            
        try:
            logger.warning(f"⚡ [LIVE TRADE] -> Submitting {action.upper()} | {amount:.4f} {symbol}")
            # order = await self.client.create_market_order(symbol, action, amount)
            # return order
            return True
        except ccxt.InsufficientFunds as e:
            logger.error(f"Insufficient funds for trade: {e}")
            return False
        except Exception as e:
            logger.error(f"Exchange API error during execution: {e}")
            return False

    async def close(self):
        """Cleanly close the CCXT async session."""
        await self.client.close()
