# run_phase6.py
import json
from src.agents.market_agent import analyze
from src.agents.strategy_agent import decide
from src.agents.critic_agent import critique
from src.risk.validator import validate_trade
from src.alpaca.portfolio import get_portfolio_state

if __name__ == "__main__":
    watchlist = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "GOOGL", "AMD"]
    portfolio = get_portfolio_state()

    print(f"\nPortfolio value: ${portfolio['portfolio_value']:,.0f} "
          f"| exposure: {portfolio['exposure_pct']*100:.0f}%")
    print(f"Scanning {len(watchlist)} symbols...\n")
    print(f"{'SYM':>6} | {'TREND':>8} | {'ACTION':>11} | {'CRITIC':>10} | RISK")
    print("-" * 60)

    approved = []

    for symbol in watchlist:
        try:
            market = analyze(symbol)
            indicators = market["indicators"]
            market_view = market["market_view"]
            thesis = decide(indicators, market_view)
            critic = critique(indicators, market_view, thesis)
            decision = validate_trade(thesis, critic, indicators, portfolio)

            action = f"{thesis.get('action')} ({float(thesis.get('confidence',0))*100:.0f}%)"
            critic_str = f"{critic.get('critic_score')}/100"

            print(f"{symbol:>6} | {market_view.get('trend'):>8} "
                  f"| {action:>11} | {critic_str:>10} | {decision['status']}")

            if decision["status"] == "APPROVED":
                approved.append((symbol, thesis, decision))

        except Exception as e:
            print(f"{symbol:>6} | ERROR: {e}")

    print("-" * 60)

    if approved:
        print(f"\n✅ {len(approved)} trade(s) APPROVED by risk engine:\n")
        for symbol, thesis, decision in approved:
            s = decision["sizing"]
            print(f"   {symbol}: {decision['action']} {s['shares']} shares "
                  f"(~${s['position_value']:,.0f}, risk ${s['risk_amount']:,.0f})")
    else:
        print("\n⚠ No trades approved this scan (all HOLD or rejected by risk).")