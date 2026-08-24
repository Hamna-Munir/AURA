# src/core/memory.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger

log = get_logger("core.memory")

DB_PATH = Path("data/aura.db")


def _connect():
    DB_PATH.parent.mkdir(exist_ok=True)   # data/ folder bana do agar nahi hai
    return sqlite3.connect(DB_PATH)


def init_db():
    """Table banao agar pehle se nahi hai."""
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            trend TEXT,
            action TEXT,
            strategy_confidence REAL,
            critic_score INTEGER,
            critic_verdict TEXT,
            risk_status TEXT,
            shares INTEGER,
            position_value REAL,
            risk_amount REAL,
            rejections TEXT,
            order_id TEXT,
            raw_json TEXT
        )
    """)
    conn.commit()
    conn.close()
    log.info("Memory DB ready at %s", DB_PATH)


def save_decision(symbol, market_view, thesis, critic, decision, order_result=None):
    """Ek poora decision (trade ho ya na ho) save karo."""
    conn = _connect()
    sizing = decision.get("sizing", {})

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "symbol": symbol,
        "trend": market_view.get("trend"),
        "action": thesis.get("action"),
        "strategy_confidence": float(thesis.get("confidence", 0)),
        "critic_score": int(critic.get("critic_score", 0)),
        "critic_verdict": critic.get("verdict"),
        "risk_status": decision.get("status"),
        "shares": sizing.get("shares", 0),
        "position_value": sizing.get("position_value", 0),
        "risk_amount": sizing.get("risk_amount", 0),
        "rejections": json.dumps(decision.get("rejections", [])),
        "order_id": order_result.get("order_id") if order_result else None,
        "raw_json": json.dumps({
            "market_view": market_view,
            "thesis": thesis,
            "critic": critic,
            "decision": decision,
        }),
    }

    conn.execute("""
        INSERT INTO decisions
        (timestamp, symbol, trend, action, strategy_confidence, critic_score,
         critic_verdict, risk_status, shares, position_value, risk_amount,
         rejections, order_id, raw_json)
        VALUES
        (:timestamp, :symbol, :trend, :action, :strategy_confidence, :critic_score,
         :critic_verdict, :risk_status, :shares, :position_value, :risk_amount,
         :rejections, :order_id, :raw_json)
    """, record)
    conn.commit()
    conn.close()
    log.info("Saved decision: %s %s -> %s", symbol, thesis.get("action"),
             decision.get("status"))


def get_all_decisions() -> list:
    """Saare decisions parho (dashboard ke liye)."""
    conn = _connect()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM decisions ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """Quick summary (dashboard ke liye)."""
    conn = _connect()
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    approved = cur.execute(
        "SELECT COUNT(*) FROM decisions WHERE risk_status='APPROVED'").fetchone()[0]
    rejected = cur.execute(
        "SELECT COUNT(*) FROM decisions WHERE risk_status='REJECTED'").fetchone()[0]
    no_trade = cur.execute(
        "SELECT COUNT(*) FROM decisions WHERE risk_status='NO_TRADE'").fetchone()[0]
    conn.close()
    return {
        "total_decisions": total,
        "approved": approved,
        "rejected": rejected,
        "no_trade": no_trade,
    }