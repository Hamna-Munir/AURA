# run_phase8.py
from src.agents.market_agent import analyze
from src.agents.strategy_agent import decide
from src.agents.critic_agent import critique
from src.risk.validator import validate_trade
from src.alpaca.portfolio import get_portfolio_state
from src.core.memory import init_db, save_decision, get_stats

if __name__ == "__main__":
    init_db()
    watchlist = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "GOOGL", "AMD"]
    portfolio = get_portfolio_state()

    print(f"\nScanning {len(watchlist)} symbols and saving to memory...\n")

    for symbol in watchlist:
        try:
            market = analyze(symbol)
            indicators = market["indicators"]
            market_view = market["market_view"]
            thesis = decide(indicators, market_view)
            critic = critique(indicators, market_view, thesis)
            decision = validate_trade(thesis, critic, indicators, portfolio)

            # save (order abhi nahi bhej rahe, sirf decisions record kar rahe)
            save_decision(symbol, market_view, thesis, critic, decision)

            print(f"{symbol:>6} | {thesis.get('action'):>4} "
                  f"| critic {critic.get('critic_score')}/100 "
                  f"| {decision['status']}")
        except Exception as e:
            print(f"{symbol:>6} | ERROR: {e}")

    print("\nMemory stats:")
    stats = get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")