# run_phase7.py
import json
import time
from src.agents.market_agent import analyze
from src.agents.strategy_agent import decide
from src.agents.critic_agent import critique
from src.risk.validator import validate_trade
from src.alpaca.portfolio import get_portfolio_state
from src.alpaca.orders import submit_order, get_order_status

if __name__ == "__main__":
    # NVDA abhi APPROVED aa raha tha — isse test karte hain.
    # (agar market band ho to bhi paper order accept ho jata hai, queue mein.)
    symbol = "NVDA"

    print(f"\n{'='*52}")
    print(f"  AURA :: Full autonomous cycle — {symbol}")
    print(f"{'='*52}\n")

    # 1-5: reasoning + risk
    market = analyze(symbol)
    indicators = market["indicators"]
    market_view = market["market_view"]
    thesis = decide(indicators, market_view)
    critic = critique(indicators, market_view, thesis)
    portfolio = get_portfolio_state()
    decision = validate_trade(thesis, critic, indicators, portfolio)

    print(f"1. MARKET   -> {market_view.get('trend')} "
          f"({float(market_view.get('confidence',0))*100:.0f}%)")
    print(f"2. STRATEGY -> {thesis.get('action')} "
          f"({float(thesis.get('confidence',0))*100:.0f}%)")
    print(f"3. CRITIC   -> {critic.get('verdict')} "
          f"(score {critic.get('critic_score')}/100)")
    print(f"4. RISK     -> {decision['status']}")

    # 6: execute only if APPROVED
    if decision["status"] == "APPROVED":
        s = decision["sizing"]
        print(f"\n   APPROVED: {decision['action']} {s['shares']} shares")
        print(f"   Submitting to Alpaca (paper)...")

        result = submit_order(symbol, s["shares"], decision["action"])
        print(f"   -> {result['status']}, order_id: {result.get('order_id')}")

        # thoda ruk kar status check karo
        if result["status"] == "SUBMITTED":
            time.sleep(2)
            status = get_order_status(result["order_id"])
            print(f"\n5. EXECUTION -> {status['status']}")
            print(f"   filled: {status['filled_qty']}/{status['qty']} "
                  f"@ {status['filled_avg_price']}")
    else:
        print(f"\n   No order sent ({decision['status']}).")
        if decision.get("rejections"):
            for r in decision["rejections"]:
                print(f"   ✗ {r}")