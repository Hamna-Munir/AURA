# src/alpaca/orders.py
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from src.alpaca.client import get_trading_client
from src.utils.logger import get_logger

log = get_logger("alpaca.orders")


def submit_order(symbol: str, qty: int, action: str,
                 order_type: str = "market") -> dict:
    """
    APPROVED trade ko Alpaca paper account par bhejo.
    action: "BUY" ya "SELL"
    """
    if qty <= 0:
        return {"status": "SKIPPED", "reason": "qty is 0"}

    client = get_trading_client()
    side = OrderSide.BUY if action.upper() == "BUY" else OrderSide.SELL

    request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.DAY,
    )

    order = client.submit_order(order_data=request)
    log.info("Order submitted: %s %s %s (id=%s)", action, qty, symbol, order.id)

    return {
        "status": "SUBMITTED",
        "order_id": str(order.id),
        "symbol": symbol,
        "qty": qty,
        "side": action.upper(),
        "order_status": str(order.status),
    }


def get_order_status(order_id: str) -> dict:
    """Order submit karne ke baad uska haal check karo (filled hua ya nahi)."""
    client = get_trading_client()
    order = client.get_order_by_id(order_id)
    return {
        "order_id": str(order.id),
        "symbol": order.symbol,
        "qty": str(order.qty),
        "side": str(order.side),
        "status": str(order.status),
        "filled_qty": str(order.filled_qty),
        "filled_avg_price": str(order.filled_avg_price) if order.filled_avg_price else None,
    }