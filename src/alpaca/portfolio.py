# src/alpaca/portfolio.py
from src.alpaca.client import get_trading_client
from src.utils.logger import get_logger

log = get_logger("alpaca.portfolio")


def get_portfolio_state() -> dict:
    """Portfolio value, cash, aur current exposure % nikaalo."""
    client = get_trading_client()
    account = client.get_account()
    positions = client.get_all_positions()

    portfolio_value = float(account.portfolio_value)
    cash = float(account.cash)

    # current exposure = sab positions ki market value ka jama
    exposure_value = sum(abs(float(p.market_value)) for p in positions)
    exposure_pct = (exposure_value / portfolio_value) if portfolio_value else 0.0

    return {
        "portfolio_value": portfolio_value,
        "cash": cash,
        "open_positions": len(positions),
        "exposure_value": round(exposure_value, 2),
        "exposure_pct": round(exposure_pct, 4),
    }