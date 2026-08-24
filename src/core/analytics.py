# src/core/analytics.py
import json
from src.core.memory import get_all_decisions


def get_dashboard_data() -> dict:
    """Memory se sab decisions parho aur dashboard ke liye ready karo."""
    rows = get_all_decisions()

    total = len(rows)
    approved = [r for r in rows if r["risk_status"] == "APPROVED"]
    rejected = [r for r in rows if r["risk_status"] == "REJECTED"]
    no_trade = [r for r in rows if r["risk_status"] == "NO_TRADE"]

    # exposure-based rejections (signature moments) alag karo
    exposure_blocks = []
    for r in rejected:
        rej = json.loads(r["rejections"]) if r["rejections"] else []
        if any("exposure" in x for x in rej):
            exposure_blocks.append(r)

    total_risk_deployed = sum(r["risk_amount"] or 0 for r in approved)

    return {
        "rows": rows,
        "total": total,
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "no_trade_count": len(no_trade),
        "exposure_blocks": len(exposure_blocks),
        "total_risk_deployed": round(total_risk_deployed, 2),
        "approved": approved,
        "rejected": rejected,
    }


def parse_row_detail(row: dict) -> dict:
    """Ek row ka raw_json khol kar poora reasoning chain nikaalo."""
    try:
        return json.loads(row["raw_json"])
    except Exception:
        return {}