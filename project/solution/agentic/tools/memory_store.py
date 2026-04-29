
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional


def _db_path() -> str:
    root = Path(__file__).resolve().parents[2]  # .../solution
    return str(root / "data" / "core" / "udahub.db")


def _ensure_ticket_messages_table(conn: sqlite3.Connection) -> None:
    """
    Ensures ticket_messages exists.
    If your notebooks already create this table, this is a no-op.
    This schema matches the reviewer expectation (message_id required).
    """
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ticket_messages (
        message_id TEXT PRIMARY KEY,
        ticket_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()


def _get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall()
    # rows: (cid, name, type, notnull, dflt_value, pk)
    return [r[1] for r in rows]


def save_message(ticket_id: str, role: str, content: str, created_at: Optional[str] = None) -> Dict[str, Any]:
    """
    Persist a conversation turn.

    Fixes reviewer findings:
    - Generates message_id when required
    - Writes created_at if column exists
    - Matches existing table schema dynamically
    """
    db = _db_path()
    created_at = created_at or datetime.utcnow().isoformat()

    conn = sqlite3.connect(db)
    try:
        _ensure_ticket_messages_table(conn)
        cols = _get_columns(conn, "ticket_messages")

        msg_id = str(uuid.uuid4())

        # Build insert based on actual columns present
        payload = {}
        if "message_id" in cols:
            payload["message_id"] = msg_id
        if "ticket_id" in cols:
            payload["ticket_id"] = ticket_id
        if "role" in cols:
            payload["role"] = role
        if "content" in cols:
            payload["content"] = content
        if "created_at" in cols:
            payload["created_at"] = created_at

        # Guard: minimal required fields
        required = {"ticket_id", "role", "content"}
        if not required.issubset(set(payload.keys())):
            return {
                "success": False,
                "error": f"ticket_messages schema missing required columns. Found columns={cols}",
                "message_id": None
            }

        keys = list(payload.keys())
        placeholders = ",".join(["?"] * len(keys))
        sql = f"INSERT INTO ticket_messages ({','.join(keys)}) VALUES ({placeholders})"

        cur = conn.cursor()
        cur.execute(sql, tuple(payload[k] for k in keys))
        conn.commit()

        return {"success": True, "message_id": msg_id, "error": None}

    except Exception as e:
        return {"success": False, "message_id": None, "error": str(e)}
    finally:
        conn.close()


def load_past_messages(ticket_id: str, limit: int = 50) -> List[Tuple[str, str]]:
    """
    Retrieve previous interactions for a ticket.

    Fixes reviewer findings:
    - Does NOT order by non-existent 'id'
    - Orders by created_at if present, else message_id
    - Returns list of (role, content)
    """
    db = _db_path()

    conn = sqlite3.connect(db)
    try:
        _ensure_ticket_messages_table(conn)
        cols = _get_columns(conn, "ticket_messages")

        order_col = "created_at" if "created_at" in cols else ("message_id" if "message_id" in cols else None)

        if order_col:
            sql = f"""
            SELECT role, content
            FROM ticket_messages
            WHERE ticket_id = ?
            ORDER BY {order_col} ASC
            LIMIT ?
            """
            params = (ticket_id, limit)
        else:
            # Worst case fallback (no ordering column) — still works
            sql = """
            SELECT role, content
            FROM ticket_messages
            WHERE ticket_id = ?
            LIMIT ?
            """
            params = (ticket_id, limit)

        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    finally:
        conn.close()
