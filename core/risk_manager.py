import logging
from typing import Dict, Any
from config.settings import SafetyLimits

logger = logging.getLogger("RiskControl")

class RiskManager:
    """
    The final gatekeeper. Ensures AI decisions do not violate user safety limits.
    """
    def __init__(self, limits: SafetyLimits):
        self.limits = limits
        self.current_daily_loss = 0.0

    def validate_trade_request(self, ai_plan: Dict[str, Any], balance: float) -> bool:
        """Evaluates an AI trade proposal against hardcoded limits."""
        symbol = ai_plan.get('symbol')
        risk_pct = ai_plan.get('recommended_risk_pct', 1.0)
        
        logger.info(f"Validating trade request for {symbol}...")

        if symbol not in self.limits.allowed_assets:
            logger.warning(f"❌ REJECTED: {symbol} is not in the allowed assets whitelist.")
            return False

        if self.current_daily_loss >= self.limits.max_daily_loss_usd:
            logger.error("❌ REJECTED: Maximum daily loss limit reached. Trading halted.")
            return False

        if risk_pct > self.limits.max_position_size_pct:
            logger.warning(
                f"⚠️ AI requested {risk_pct*100}% risk, which exceeds limit of "
                f"{self.limits.max_position_size_pct*100}%. Scaling down trade."
            )
            # We scale down the risk to the maximum allowed instead of rejecting
            ai_plan['recommended_risk_pct'] = self.limits.max_position_size_pct

        logger.info("✅ Risk validation passed.")
        return True
