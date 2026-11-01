import json
from typing import Optional, Dict, Any
from backend.database import get_db_connection

def log_audit_event(
    thread_id: str,
    action: str,
    tool_name: str,
    params: Dict[str, Any],
    required_approval: bool,
    approval_status: str,
    result: Optional[Any] = None,
    error: Optional[str] = None,
    user_role: str = "operator",
) -> int:
    """Record an audit trail entry in SQLite."""
    params_json = json.dumps(params, default=str)
    result_json = json.dumps(result, default=str) if result is not None else None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs 
            (thread_id, user_role, action, tool_name, params, required_approval, approval_status, result, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (thread_id, user_role, action, tool_name, params_json, 1 if required_approval else 0, approval_status, result_json, error)
        )
        conn.commit()
        return cursor.lastrowid

def get_audit_logs(limit: int = 50, thread_id: Optional[str] = None):
    """Retrieve recent audit events for compliance review."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if thread_id:
            cursor.execute(
                "SELECT * FROM audit_logs WHERE thread_id = ? ORDER BY log_id DESC LIMIT ?",
                (thread_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT ?",
                (limit,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
