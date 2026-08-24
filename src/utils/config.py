# src/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"
LLM_API_KEY = os.getenv("LLM_API_KEY")


def validate_config():
    """Startup par hi loudly fail ho agar kuch missing ya unsafe hai."""
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        raise RuntimeError(
            "Alpaca keys missing hain. .env file mein apni PAPER keys daalo."
        )
    # SAFETY GUARD: AURA live-money account par chalne se inkaar karti hai.
    if not ALPACA_PAPER:
        raise RuntimeError(
            "ALPACA_PAPER true nahi hai. AURA sirf paper trading demo hai "
            "aur live account par nahi chalegi. .env mein ALPACA_PAPER=true set karo."
        )