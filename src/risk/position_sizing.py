# src/risk/position_sizing.py
from src.risk.limits import RISK_LIMITS


def calculate_position_size(portfolio_value: float, price: float,
                            stop_loss_distance: float) -> dict:
    """
    Risk-based sizing:
      risk_amount = portfolio * 1%
      shares = risk_amount / stop_distance
    Phir max-position-% cap lagao.
    """
    risk_amount = portfolio_value * RISK_LIMITS["risk_per_trade_pct"]

    if stop_loss_distance <= 0:
        return {"shares": 0, "reason": "invalid stop_loss_distance"}

    raw_shares = risk_amount / stop_loss_distance
    position_value = raw_shares * price

    # max position cap
    max_position_value = portfolio_value * RISK_LIMITS["max_position_pct"]
    if position_value > max_position_value:
        capped_shares = max_position_value / price
        return {
            "shares": int(capped_shares),
            "risk_amount": round(risk_amount, 2),
            "position_value": round(int(capped_shares) * price, 2),
            "capped": True,
        }

    return {
        "shares": int(raw_shares),
        "risk_amount": round(risk_amount, 2),
        "position_value": round(int(raw_shares) * price, 2),
        "capped": False,
    }