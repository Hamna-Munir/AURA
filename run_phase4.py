# run_phase4.py
import json
from src.agents.market_agent import analyze
from src.agents.strategy_agent import decide

if __name__ == "__main__":
    symbol = "AAPL"

    # Phase 3: market view
    market = analyze(symbol)
    indicators = market["indicators"]
    market_view = market["market_view"]

    # Phase 4: trade thesis
    thesis = decide(indicators, market_view)

    print(f"\n=== AURA :: Strategy Agent — {symbol} ===\n")
    print("Market view:")
    print(json.dumps(market_view, indent=2))
    print("\nTrade thesis:")
    print(json.dumps(thesis, indent=2))