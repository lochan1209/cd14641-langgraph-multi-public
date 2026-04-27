
import os
import re
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")

def _db_path() -> str:
    # .../solution/agentic/tools/account_lookup_tool.py -> parents[2] = .../solution
    root = Path(__file__).resolve().parents[2]
    return str(root / "data" / "external" / "cultpass.db")

def _extract_email(text: str) -> Optional[str]:
    m = EMAIL_RE.search(text or "")
    return m.group(0) if m else None

def _normalize_email(s: str) -> str:
    """
    Aggressive normalization to defeat hidden whitespace/quotes/brackets.
    Handles: quotes, <>, tabs, newlines, multiple spaces, NBSP.
    """
    if s is None:
        return ""
    s = str(s)
    s = s.strip().lower()
    s = s.strip("'\"<>")
    # collapse whitespace and remove non-breaking spaces
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", "", s)  # remove ALL whitespace
    return s

def lookup_account(query_or_email: str) -> Dict[str, Any]:
    """
    Tool #2: Account lookup + subscription info from CultPass external DB.

    Robust strategy:
    1) Read users table (user_id, email, full_name, is_blocked, created_at)
    2) Normalize emails in Python and match
    3) Fetch subscription by user_id

    Returns:
      {
        "found": bool,
        "email": str|None,
        "user": {...}|None,
        "subscription": {...}|None,
        "error": str|None,
        "debug": {
            "db_path": str,
            "tables": [...],
            "total_users": int,
            "sample_emails": [...]
        }
      }
    """
    
    def _is_email_only(text: str) -> bool:
        return bool(re.fullmatch(r"[\w\.-]+@[\w\.-]+\.\w+", (text or "").strip()))

    # ✅ FIX: if input is a pure email, use it; otherwise extract with regex
    if _is_email_only(query_or_email):
        raw_email = query_or_email.strip()
    else:
        raw_email = _extract_email(query_or_email)

    email = _normalize_email(raw_email) if raw_email else ""


    db = _db_path()
    if not email:
        return {
            "found": False,
            "email": None,
            "user": None,
            "subscription": None,
            "error": "No email found. Provide a customer email (e.g., user@example.com).",
            "debug": {"db_path": db, "tables": [], "total_users": 0, "sample_emails": []}
        }

    if not os.path.exists(db):
        return {
            "found": False,
            "email": email,
            "user": None,
            "subscription": None,
            "error": f"CultPass database not found at {db}. Run 01_external_db_setup.ipynb.",
            "debug": {"db_path": db, "tables": [], "total_users": 0, "sample_emails": []}
        }

    conn = None
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]

        if "users" not in tables:
            return {
                "found": False,
                "email": email,
                "user": None,
                "subscription": None,
                "error": f"'users' table not found. Tables={tables}",
                "debug": {"db_path": db, "tables": tables, "total_users": 0, "sample_emails": []}
            }

        # Load all users (small dataset, safe for project scale)
        cur.execute("SELECT user_id, full_name, email, is_blocked, created_at FROM users")
        rows = cur.fetchall()
        total_users = len(rows)
        sample_emails = [r[2] for r in rows[:5]]

        # Build normalized email -> user row map
        email_map: Dict[str, Tuple] = {}
        for r in rows:
            stored_email_norm = _normalize_email(r[2])
            if stored_email_norm:
                email_map[stored_email_norm] = r

        if email not in email_map:
            # For extra help, show a few normalized keys too
            return {
                "found": False,
                "email": raw_email,
                "user": None,
                "subscription": None,
                "error": "No user found for this email (after Python normalization).",
                "debug": {
                    "db_path": db,
                    "tables": tables,
                    "total_users": total_users,
                    "sample_emails": sample_emails,
                }
            }

        row = email_map[email]
        user = {
            "user_id": row[0],
            "full_name": row[1],
            "email": row[2],
            "is_blocked": bool(row[3]),
            "created_at": row[4],
        }

        subscription = None
        if "subscriptions" in tables:
            cur.execute(
                "SELECT subscription_id, status, tier, monthly_quota, started_at "
                "FROM subscriptions WHERE user_id = ? ORDER BY started_at DESC LIMIT 1",
                (user["user_id"],)
            )
            srow = cur.fetchone()
            if srow:
                subscription = {
                    "subscription_id": srow[0],
                    "status": srow[1],
                    "tier": srow[2],
                    "monthly_quota": srow[3],
                    "started_at": srow[4],
                }

        return {
            "found": True,
            "email": user["email"],
            "user": user,
            "subscription": subscription,
            "error": None,
            "debug": {
                "db_path": db,
                "tables": tables,
                "total_users": total_users,
                "sample_emails": sample_emails,
            }
        }

    except Exception as e:
        return {
            "found": False,
            "email": raw_email,
            "user": None,
            "subscription": None,
            "error": f"DB query failed: {str(e)}",
            "debug": {"db_path": db, "tables": [], "total_users": 0, "sample_emails": []}
        }
    finally:
        if conn:
            conn.close()
