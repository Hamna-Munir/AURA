# src/risk/limits.py
# AURA ke deterministic risk limits. Ye LLM decide NAHI karta.

RISK_LIMITS = {
    "max_position_pct": 0.10,       # ek position max 10% portfolio
    "risk_per_trade_pct": 0.01,     # ek trade max 1% risk
    "min_confidence": 0.65,         # 0.75 -> 0.65 (LLM ke liye realistic)
    "min_risk_reward": 2.0,         # R/R floor
    "max_exposure_pct": 0.30,   # demo scenario: 30% cap taake "refuse" moment dikhe
    "min_critic_score": 50,         # ab critic full range deta hai, to 50 = "review pass"
}