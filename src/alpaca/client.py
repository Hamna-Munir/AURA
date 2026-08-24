# src/alpaca/client.py
from alpaca.trading.client import TradingClient
from src.utils import config
from src.utils.logger import get_logger

log = get_logger("alpaca.client")


def get_trading_client() -> TradingClient:
    """Config validate karke ek paper TradingClient return karta hai."""
    config.validate_config()
    client = TradingClient(
        api_key=config.ALPACA_API_KEY,
        secret_key=config.ALPACA_SECRET_KEY,
        paper=config.ALPACA_PAPER,   # guard ki wajah se hamesha True
    )
    return client


def get_account_summary() -> dict:
    """Connection prove karo: cash, buying power, portfolio value parho."""
    client = get_trading_client()
    acct = client.get_account()

    summary = {
        "account_number": acct.account_number,
        "status": str(acct.status),
        "cash": float(acct.cash),
        "buying_power": float(acct.buying_power),
        "portfolio_value": float(acct.portfolio_value),
        "currency": acct.currency,
    }
    log.info("Alpaca paper account connected: %s", summary["account_number"])
    return summary