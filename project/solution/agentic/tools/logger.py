
import sqlite3
from pathlib import Path
import json
from datetime import datetime

def log_event(ticket_id, stage, payload):
    db = Path(__file__).resolve().parents[2] / "data/core/udahub.db"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO ticket_logs (ticket_id, stage, payload, created_at)
    VALUES (?, ?, ?, ?)
    """, (ticket_id, stage, json.dumps(payload), datetime.utcnow()))

    conn.commit()
    conn.close()
