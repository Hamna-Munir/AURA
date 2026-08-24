# src/core/orchestrator.py
from src.agents.market_agent import analyze
from src.agents.strategy_agent import decide
from src.agents.critic_agent import critique
from src.risk.validator import validate_trade
from src.alpaca.portfolio import get_portfolio_state
from src.alpaca.orders import submit_order
from src.core.memory import init_db, save_decision
from src.utils.logger import get_logger

log = get_logger("core.orchestrator")

DEFAULT_WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "GOOGL", "AMD"]


def run_cycle(watchlist=None, execute=False):
    """
    Ek poora autonomous cycle:
      scan -> reason -> critique -> risk-check -> (execute) -> remember
    execute=True  -> APPROVED trades Alpaca (paper) par bhejta hai
    execute=False -> sirf decisions leta hai, order nahi bhejta (dry run)

    Running exposure track karta hai: jaise trades approve hoti hain,
    portfolio ka exposure barhta hai — is se risk engine baad wale trades
    ko exposure limit par rok sakta hai (signature "AURA refuses" moment).
    """
    init_db()
    watchlist = watchlist or DEFAULT_WATCHLIST
    portfolio = get_portfolio_state()

    results = []
    approved_count = 0
    rejected_count = 0
    executed_count = 0

    log.info("=== AURA cycle start | portfolio $%.0f | exposure %.0f%% | execute=%s ===",
             portfolio["portfolio_value"], portfolio["exposure_pct"] * 100, execute)

    for symbol in watchlist:
        try:
            # --- reasoning chain ---
            market = analyze(symbol)
            indicators = market["indicators"]
            market_view = market["market_view"]
            thesis = decide(indicators, market_view)
            critic = critique(indicators, market_view, thesis)

            # --- risk gate (current running portfolio state ke against) ---
            decision = validate_trade(thesis, critic, indicators, portfolio)

            order_result = None

            if decision["status"] == "APPROVED":
                approved_count += 1
                sizing = decision["sizing"]

                # execute if allowed
                if execute:
                    order_result = submit_order(symbol, sizing["shares"],
                                                decision["action"])
                    if order_result.get("status") == "SUBMITTED":
                        executed_count += 1

                # running exposure update karo (agar ye trade lete to)
                portfolio["exposure_value"] += sizing.get("position_value", 0)
                portfolio["exposure_pct"] = (
                    portfolio["exposure_value"] / portfolio["portfolio_value"]
                )

            elif decision["status"] == "REJECTED":
                rejected_count += 1

            # --- remember (har decision, trade ho ya na ho) ---
            save_decision(symbol, market_view, thesis, critic, decision, order_result)

            results.append({
                "symbol": symbol,
                "action": thesis.get("action"),
                "critic_score": critic.get("critic_score"),
                "status": decision["status"],
                "rejections": decision.get("rejections", []),
                "running_exposure": round(portfolio["exposure_pct"], 4),
                "order": order_result,
            })

        except Exception as e:
            log.error("Cycle error for %s: %s", symbol, e)
            results.append({"symbol": symbol, "status": "ERROR", "error": str(e)})

    log.info("=== AURA cycle done | approved=%d rejected=%d executed=%d ===",
             approved_count, rejected_count, executed_count)

    return {
        "portfolio_start_exposure": 0,
        "portfolio_end_exposure": round(portfolio["exposure_pct"], 4),
        "approved": approved_count,
        "rejected": rejected_count,
        "executed": executed_count,
        "results": results,
    }