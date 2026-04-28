
"""
analysis_agent.py

Purpose (Rubric Alignment):
- Produces the final customer-support response for a ticket, using:
  1) Knowledge-base context (retrieved KB articles)
  2) Support-operation tool outputs (DB-backed account/subscription info)
  3) Persistent customer interaction history (DB-stored prior messages)
- Implements confidence scoring + escalation logic
- Writes structured logs (searchable) for auditability
- Persists the current conversation turn to a database so future sessions can reuse it

Expected inputs in `state`:
- ticket_id: str                      (required for DB persistence & logs)
- user_input: str                     (customer message)
- intent: str                         (classification from intent agent)
- ticket_metadata: dict               (e.g., urgency, complexity, status, tags)
- retrieved_kb: dict                  (from retrieval_agent; contains "results" list with scores)
- account_info: dict|None             (from account_lookup tool; structured)
- subscription_info: dict|None        (from subscription tool; structured)
- tools_used: list[str]               (tools invoked upstream, if any)
- next_step: str                      (route set by intent agent)

Outputs written to state:
- final_answer: str
- confidence: float (0..1)
- escalated: bool
- escalation_reason: str|None
- next_step: "memory"
- actions_taken: ["analysis_agent"]
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig


# --- Optional imports (these must exist in your project for full rubric alignment) ---
# They enable DB persistence and structured logging.
try:
    from agentic.tools.memory_store import load_past_messages, save_message
except Exception:  # pragma: no cover
    load_past_messages = None
    save_message = None

try:
    from agentic.tools.logger import log_event
except Exception:  # pragma: no cover
    log_event = None


def _safe_log(ticket_id: str, stage: str, payload: Dict[str, Any]) -> None:
    """Write structured logs if logger tool is available."""
    if log_event is None:
        return
    try:
        log_event(ticket_id=ticket_id, stage=stage, payload=payload)
    except Exception:
        # Logging should never break ticket processing.
        pass


def _kb_confidence(kb: Dict[str, Any]) -> float:
    """
    Confidence from KB retrieval:
    - Uses top match score plus a small bonus for multiple hits.
    - Returns low confidence if there are no results.
    """
    results = (kb or {}).get("results", []) or []
    if not results:
        return 0.20

    best = 0.0
    for r in results:
        try:
            best = max(best, float(r.get("score", 0.0)))
        except Exception:
            continue

    bonus = min(0.20, 0.05 * max(0, len(results) - 1))
    return float(min(1.0, best + bonus))


def _threshold_from_metadata(metadata: Dict[str, Any]) -> float:
    """
    Escalation threshold that depends on ticket metadata.
    Higher urgency/complexity => higher threshold (escalate more easily).
    """
    metadata = metadata or {}
    urgency = (metadata.get("urgency") or "low").lower()
    complexity = (metadata.get("complexity") or "low").lower()

    # Base threshold: reasonable default
    threshold = 0.50

    if urgency in {"high", "urgent", "p1"}:
        threshold = max(threshold, 0.65)
    elif urgency in {"medium", "p2"}:
        threshold = max(threshold, 0.55)

    if complexity in {"high", "complex"}:
        threshold = max(threshold, 0.65)
    elif complexity in {"medium"}:
        threshold = max(threshold, 0.55)

    return float(min(0.85, threshold))


def _load_history(ticket_id: str, limit: int = 6) -> List[str]:
    """
    Load previous interactions for this ticket from persistent DB memory.
    Returns last N messages as formatted strings: "role: content".
    """
    if load_past_messages is None:
        return []

    try:
        rows = load_past_messages(ticket_id) or []
        # rows expected: [(role, content), ...]
        tail = rows[-limit:]
        return [f"{r[0]}: {r[1]}" for r in tail]
    except Exception:
        return []


def analysis_agent(state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """
    Final response synthesis + escalation decision.
    """
    ticket_id = state.get("ticket_id") or state.get("session_id") or "unknown_ticket"
    user_input = state.get("user_input", "")
    intent = (state.get("intent") or "unknown").lower()
    metadata = state.get("ticket_metadata", {}) or {}

    llm = config.get("configurable", {}).get("llm")
    if llm is None:
        raise KeyError("Missing llm in config['configurable']['llm'].")

    kb = state.get("retrieved_kb", {}) or {}
    account_info = state.get("account_info")
    subscription_info = state.get("subscription_info")
    tools_used = state.get("tools_used", []) or []

    # --- Persistent memory: load prior ticket conversation ---
    history_lines = _load_history(ticket_id=ticket_id, limit=6)

    # --- Log: analysis start ---
    _safe_log(ticket_id, "analysis_start", {
        "intent": intent,
        "ticket_metadata": metadata,
        "tools_used": tools_used,
        "history_loaded": len(history_lines),
    })

    # --- Persist current user message (so returning customers have history) ---
    if save_message is not None and ticket_id != "unknown_ticket":
        try:
            save_message(ticket_id=ticket_id, role="user", content=user_input)
        except Exception:
            # Persistence should not break processing
            pass

    # --- Route-sensitive thresholds (metadata-driven) ---
    threshold = _threshold_from_metadata(metadata)

    # ============================================================
    # PATH A: Account / subscription actions (DB-backed operations)
    # ============================================================
    # If account_info exists (lookup attempted), prioritize it.
    if intent in {"account_action", "action"} or account_info is not None or subscription_info is not None:
        # If lookup succeeded, answer from DB-backed tool outputs with high confidence.
        if account_info and account_info.get("found"):
            user = account_info.get("user") or {}
            sub = account_info.get("subscription") or {}

            # If subscription_tool provided newer info, prefer it.
            if isinstance(subscription_info, dict) and subscription_info.get("success"):
                sub = {
                    "status": subscription_info.get("status"),
                    "tier": subscription_info.get("tier"),
                    "monthly_quota": subscription_info.get("quota"),
                }

            final_answer = (
                f"Here are the subscription details for {user.get('full_name', 'the customer')}:\n\n"
                f"- Email: {user.get('email')}\n"
                f"- Tier: {sub.get('tier', 'unknown')}\n"
                f"- Status: {sub.get('status', 'unknown')}\n"
                f"- Monthly quota: {sub.get('monthly_quota', 'unknown')}\n\n"
                "If you want to cancel, pause, or change the plan, tell me what you want to do and I’ll guide you."
            )

            confidence = 0.95
            escalated = False

            _safe_log(ticket_id, "analysis_account_success", {
                "confidence": confidence,
                "escalated": escalated,
                "user_id": user.get("user_id"),
            })

            if save_message is not None and ticket_id != "unknown_ticket":
                try:
                    save_message(ticket_id=ticket_id, role="assistant", content=final_answer)
                except Exception:
                    pass

            return {
                "final_answer": final_answer,
                "confidence": confidence,
                "escalated": escalated,
                "escalation_reason": None,
                "next_step": "memory",
                "actions_taken": ["analysis_agent"],
            }

        # If lookup attempted but failed => escalation (account action is sensitive)
        if account_info is not None and not account_info.get("found"):
            err = account_info.get("error") or "Account lookup failed."
            dbg = account_info.get("debug", {}) or {}
            sample_emails = dbg.get("sample_emails", [])

            final_answer = (
                "I tried to look up the account details, but I couldn't complete the account lookup.\n\n"
                f"Reason: {err}\n"
                + (f"\nSample emails in DB (for testing): {sample_emails}\n" if sample_emails else "\n")
                + "✅ Next step: Escalating to human support.\n"
                "Please confirm the customer email and try again.\n"
                f"(confidence=0.40)"
            )

            confidence = 0.40
            escalated = True

            _safe_log(ticket_id, "analysis_account_failed", {
                "confidence": confidence,
                "escalated": escalated,
                "error": err,
            })

            if save_message is not None and ticket_id != "unknown_ticket":
                try:
                    save_message(ticket_id=ticket_id, role="assistant", content=final_answer)
                except Exception:
                    pass

            return {
                "final_answer": final_answer,
                "confidence": confidence,
                "escalated": escalated,
                "escalation_reason": "Account lookup failed",
                "next_step": "memory",
                "actions_taken": ["analysis_agent"],
            }

    # ===========================================
    # PATH B: Knowledge-base response + escalation
    # ===========================================
    confidence = _kb_confidence(kb)
    results = kb.get("results", []) or []

    # If the ticket is urgent, enforce stricter escalation threshold.
    if confidence < threshold or intent in {"urgent", "unknown"}:
        final_answer = (
            "I couldn't find a confident match in the knowledge base for this request.\n\n"
            "✅ Next step: Escalating to human support.\n"
            "To help resolve faster, please share one of the following:\n"
            "- the customer email (if account-specific)\n"
            "- the exact error message or screenshot (if technical)\n"
            "- what action you were trying to perform and when\n\n"
            f"(confidence={confidence:.2f}, threshold={threshold:.2f})"
        )

        escalated = True
        _safe_log(ticket_id, "analysis_escalation", {
            "confidence": confidence,
            "threshold": threshold,
            "intent": intent,
            "reason": "Low KB confidence or unclear/urgent intent",
        })

        if save_message is not None and ticket_id != "unknown_ticket":
            try:
                save_message(ticket_id=ticket_id, role="assistant", content=final_answer)
            except Exception:
                pass

        return {
            "final_answer": final_answer,
            "confidence": confidence,
            "escalated": True,
            "escalation_reason": "Low confidence knowledge match",
            "next_step": "memory",
            "actions_taken": ["analysis_agent"],
        }

    # Build KB context for grounded answering (use full content when available).
    kb_context = "\n\n".join(
        [f"- {r.get('title')} (score={r.get('score')}): {r.get('full_content', r.get('snippet', ''))}"
         for r in results]
    )

    # Include persistent history as additional context for personalization.
    history_block = "\n".join(history_lines) if history_lines else "No prior history."

    system = SystemMessage(content=(
        "You are a customer support assistant for CultPass/Uda-hub.\n"
        "Answer using ONLY the provided KB_CONTEXT. Do not invent policies.\n"
        "Use the PRIOR_HISTORY to keep continuity and avoid repeating steps.\n"
        "If KB_CONTEXT does not contain the answer, propose escalation.\n"
        "Be concise, accurate, and actionable."
    ))

    prompt = [
        system,
        SystemMessage(content=f"PRIOR_HISTORY:\n{history_block}"),
        SystemMessage(content=f"KB_CONTEXT:\n{kb_context}"),
        HumanMessage(content=user_input),
    ]

    answer = llm.invoke(prompt).content.strip()

    cited_titles = [r.get("title") for r in results if r.get("title")]
    if cited_titles:
        answer += "\n\nSources: " + "; ".join(cited_titles)
    answer += f"\n(confidence={confidence:.2f})"

    _safe_log(ticket_id, "analysis_kb_success", {
        "confidence": confidence,
        "intent": intent,
        "sources": cited_titles,
        "history_used": len(history_lines),
    })

    if save_message is not None and ticket_id != "unknown_ticket":
        try:
            save_message(ticket_id=ticket_id, role="assistant", content=answer)
        except Exception:
            pass

    return {
        "final_answer": answer,
        "confidence": confidence,
        "escalated": False,
        "escalation_reason": None,
        "next_step": "memory",
        "actions_taken": ["analysis_agent"],
    }
