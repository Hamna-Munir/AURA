# run_phase5.py
import json
from src.agents.market_agent import analyze
from src.agents.strategy_agent import decide
from src.agents.critic_agent import critique

if __name__ == "__main__":
    symbol = "AAPL"

    market = analyze(symbol)
    indicators = market["indicators"]
    market_view = market["market_view"]

    thesis = decide(indicators, market_view)
    critic = critique(indicators, market_view, thesis)

    print(f"\n{'='*50}")
    print(f"  AURA :: Full reasoning chain — {symbol}")
    print(f"{'='*50}\n")

    print(f"1. MARKET AGENT   -> {market_view.get('trend')} "
          f"({float(market_view.get('confidence', 0))*100:.0f}%)")
    print(f"2. STRATEGY AGENT -> {thesis.get('action')} "
          f"({float(thesis.get('confidence', 0))*100:.0f}%)")
    print(f"   reason: {thesis.get('entry_reason')}")
    print(f"3. CRITIC AGENT   -> {critic.get('verdict')} "
          f"(score {critic.get('critic_score')}/100)")
    print(f"   strongest risk: {critic.get('strongest_risk')}\n")

    print("Critic's counter-arguments:")
    for arg in critic.get("counter_arguments", []):
        print(f"   - {arg}")

    print("\nFull critic JSON:")
    print(json.dumps(critic, indent=2))