# run_phase2.py
from src.alpaca.market_data import compute_indicators

if __name__ == "__main__":
    symbol = "AAPL"
    summary = compute_indicators(symbol)
    print(f"\n=== AURA :: Market snapshot for {summary['symbol']} ===")
    for k, v in summary.items():
        print(f"{k:>14}: {v}")