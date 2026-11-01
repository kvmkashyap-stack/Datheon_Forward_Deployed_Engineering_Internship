import hashlib
import json
from typing import Optional, Dict, Any, Tuple
from backend.database import get_db_connection

def compute_params_hash(action: str, params: Dict[str, Any]) -> str:
    """Generate SHA-256 fingerprint for action and arguments."""
    serialized = json.dumps({"action": action, "params": params}, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def check_idempotency(idempotency_key: Optional[str], action: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return cached result if this exact operation was already executed."""
    if not idempotency_key:
        # If no explicit key provided, check by params hash
        key = compute_params_hash(action, params)
    else:
        key = idempotency_key

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT result FROM idempotency_records WHERE idempotency_key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return json.loads(row["result"])
    return None

def record_idempotency(idempotency_key: Optional[str], action: str, params: Dict[str, Any], result: Dict[str, Any]):
    """Persist execution outcome under idempotency key."""
    if not idempotency_key:
        key = compute_params_hash(action, params)
    else:
        key = idempotency_key

    params_hash = compute_params_hash(action, params)
    result_str = json.dumps(result, default=str)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO idempotency_records (idempotency_key, action, params_hash, result)
            VALUES (?, ?, ?, ?)
            """,
            (key, action, params_hash, result_str)
        )
        conn.commit()
