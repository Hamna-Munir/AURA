# src/risk/validator.py
from src.risk.limits import RISK_LIMITS
from src.risk.position_sizing import calculate_position_size
from src.utils.logger import get_logger

log = get_logger("risk.validator")


def validate_trade(thesis: dict, critic: dict, indicators: dict,
                   portfolio: dict) -> dict:
    """
    Deterministic risk gate. AI ki koi baat yahan override nahi karti.
    Returns: status = APPROVED / REJECTED / NO_TRADE, + reasons + sizing.
    """
    action = thesis.get("action", "HOLD")
    checks = []
    rejections = []

    # 0. HOLD par koi trade nahi
    if action == "HOLD":
        return {
            "status": "NO_TRADE",
            "reason": "Strategy Agent chose HOLD — no trade to validate.",
            "checks": [],
        }

    confidence = float(thesis.get("confidence", 0))
    rr = float(thesis.get("expected_risk_reward", 0))
    critic_score = int(critic.get("critic_score", 0))

    # 1. confidence check
    if confidence >= RISK_LIMITS["min_confidence"]:
        checks.append(f"PASS confidence {confidence:.2f} >= {RISK_LIMITS['min_confidence']}")
    else:
        rejections.append(f"confidence {confidence:.2f} < {RISK_LIMITS['min_confidence']}")

    # 2. risk/reward check
    if rr >= RISK_LIMITS["min_risk_reward"]:
        checks.append(f"PASS risk/reward {rr} >= {RISK_LIMITS['min_risk_reward']}")
    else:
        rejections.append(f"risk/reward {rr} < {RISK_LIMITS['min_risk_reward']}")

    # 3. critic score check (adversarial layer ka hard rule)
    if critic_score >= RISK_LIMITS["min_critic_score"]:
        checks.append(f"PASS critic score {critic_score} >= {RISK_LIMITS['min_critic_score']}")
    else:
        rejections.append(f"critic score {critic_score} < {RISK_LIMITS['min_critic_score']}")

    # 4. position sizing
    sizing = calculate_position_size(
        portfolio["portfolio_value"], indicators["price"],
        float(thesis.get("stop_loss_distance", 0)),
    )
    if sizing["shares"] <= 0:
        rejections.append("position size computed as 0 shares")

    # 5. exposure check (naya trade add karne ke baad)
    new_exposure_value = portfolio["exposure_value"] + sizing.get("position_value", 0)
    new_exposure_pct = new_exposure_value / portfolio["portfolio_value"]
    if new_exposure_pct <= RISK_LIMITS["max_exposure_pct"]:
        checks.append(f"PASS exposure {new_exposure_pct:.2f} <= {RISK_LIMITS['max_exposure_pct']}")
    else:
        rejections.append(
            f"exposure would be {new_exposure_pct:.2f} > {RISK_LIMITS['max_exposure_pct']}")

    # final verdict
    if rejections:
        status = "REJECTED"
        log.info("Trade REJECTED: %s", "; ".join(rejections))
    else:
        status = "APPROVED"
        log.info("Trade APPROVED: %s %s shares", action, sizing["shares"])

    return {
        "status": status,
        "action": action,
        "symbol": thesis.get("symbol"),
        "sizing": sizing,
        "new_exposure_pct": round(new_exposure_pct, 4),
        "checks_passed": checks,
        "rejections": rejections,
    }