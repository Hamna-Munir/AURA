# run_phase1.py
from src.alpaca.client import get_account_summary

if __name__ == "__main__":
    summary = get_account_summary()
    print("\n=== AURA :: Alpaca connection OK ===")
    for k, v in summary.items():
        print(f"{k:>18}: {v}")