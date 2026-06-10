import asyncio
import logging
from config.settings import AppConfig, SafetyLimits
from ai.deepseek_client import DeepSeekV4Client
from exchanges.ccxt_wrapper import ExchangeWrapper
from core.risk_manager import RiskManager

logger = logging.getLogger("Engine")

class SignalcraftEngine:
    """
    The main orchestrator. Ties together market data, AI reasoning, and exchange execution.
    """
    def __init__(self, config: AppConfig, limits: SafetyLimits):
        self.config = config
        self.limits = limits
        self.is_running = False
        
        # Initialize modules
        self.ai = DeepSeekV4Client(config.deepseek_api_key)
        self.exchange = ExchangeWrapper(
            exchange_id=config.exchange_id,
            api_key=config.exchange_api_key,
            secret=config.exchange_secret,
            is_paper=config.paper_trading_mode
        )
        self.risk_manager = RiskManager(limits)

    async def _request_manual_confirmation(self, trade_plan: dict) -> bool:
        """Simulates the GUI manual confirmation step required by Signalcraft design."""
        print("\n" + "="*60)
        print("🛑 SIGNALCRAFT: MANUAL CONFIRMATION REQUIRED 🛑")
        print(f"Asset:   {trade_plan['symbol']}")
        print(f"Action:  {trade_plan['action'].upper()} @ ${trade_plan['entry_price']}")
        print(f"Risk:    {trade_plan['recommended_risk_pct']*100}% of portfolio")
        print(f"Reason:  {trade_plan['reasoning']}")
        print("="*60)
        # Simulating user clicking "Approve" after reading
        await asyncio.sleep(1)
        print("[System] -> User approved trade execution.\n")
        return True

    async def start_monitoring(self):
        """The main asynchronous 24/7 event loop."""
        self.is_running = True
        logger.info("Starting Signalcraft Engine...")
        
        try:
            # We will run 3 iterations just for demonstration purposes
            for cycle in range(1, 4):
                logger.info(f"--- Monitoring Cycle {cycle} ---")
                
                for symbol in self.limits.allowed_assets:
                    # 1. Fetch raw data
                    market_data = await self.exchange.fetch_market_data(symbol)
                    if not market_data: continue

                    # 2. Level 1 AI: Flash Scan
                    flash_alert = await self.ai.analyze_tick_flash(market_data)
                    
                    if flash_alert:
                        # 3. Level 2 AI: Deep Pro Analysis
                        trade_plan = await self.ai.analyze_setup_pro_max(
                            flash_signal=flash_alert,
                            thesis=self.config.user_thesis
                        )
                        
                        if trade_plan and trade_plan.get('approved'):
                            # 4. Check Observer vs Execution mode
                            if not self.config.execution_mode_enabled:
                                logger.info(f"🔍 [OBSERVER MODE] Setup found on {symbol}. Execution disabled. Logging to journal.")
                                continue
                                
                            # 5. Pass through Risk Manager
                            balance = await self.exchange.get_portfolio_balance_usd()
                            if self.risk_manager.validate_trade_request(trade_plan, balance):
                                
                                # 6. Await Manual Human Confirmation
                                if await self._request_manual_confirmation(trade_plan):
                                    
                                    # 7. Calculate position size and Execute
                                    usd_size = balance * trade_plan['recommended_risk_pct']
                                    crypto_amount = usd_size / trade_plan['entry_price']
                                    
                                    await self.exchange.place_market_order(
                                        action=trade_plan['action'],
                                        symbol=trade_plan['symbol'],
                                        amount=crypto_amount
                                    )

                await asyncio.sleep(2) # Delay between cycles
                
        except Exception as e:
            logger.critical(f"Engine encountered a fatal error: {e}")
        finally:
            await self.exchange.close()
            logger.info("Signalcraft Engine safely shut down.")
