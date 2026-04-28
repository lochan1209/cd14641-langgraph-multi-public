
import sqlite3
from pathlib import Path

def save_message(ticket_id, role, content):
    db = Path(__file__).resolve().parents[2] / "data/core/udahub.db"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO ticket_messages (ticket_id, role, content)
    VALUES (?, ?, ?)
    """, (ticket_id, role, content))

    conn.commit()
    conn.close()


def load_past_messages(ticket_id):
    db = Path(__file__).resolve().parents[2] / "data/core/udahub.db"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
    SELECT role, content FROM ticket_messages
    WHERE ticket_id = ?
    ORDER BY id ASC
    """, (ticket_id,))

    rows = cur.fetchall()
    conn.close()

    return rows
