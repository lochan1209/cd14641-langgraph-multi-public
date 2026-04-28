
import sqlite3
from pathlib import Path

def get_subscription_status(user_id):
    db = Path(__file__).resolve().parents[2] / "data/external/cultpass.db"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
        SELECT status, tier, monthly_quota
        FROM subscriptions
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"success": False, "error": "No subscription found"}

    return {
        "success": True,
        "status": row[0],
        "tier": row[1],
        "quota": row[2]
    }
