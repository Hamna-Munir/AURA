# run_phase3.py
import json
from src.agents.market_agent import analyze

if __name__ == "__main__":
    symbol = "AAPL"
    output = analyze(symbol)

    print(f"\n=== AURA :: Market Agent — {symbol} ===\n")
    print("Indicators fed to AI:")
    print(json.dumps(output["indicators"], indent=2))
    print("\nMarket Agent judgment:")
    print(json.dumps(output["market_view"], indent=2))