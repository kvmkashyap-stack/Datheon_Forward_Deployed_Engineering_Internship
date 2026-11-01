import time
import uuid
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from backend.database import get_db_connection
from backend.safety.validator import LeadLookupSchema, LeadStatusUpdateSchema, CreateTicketSchema
from backend.safety.idempotency import check_idempotency, record_idempotency

def retry_operation(func, max_retries: int = 3, backoff_factor: float = 0.5):
    """Execute function with retries and exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(backoff_factor * (2 ** attempt))

@tool("lookup_customer_lead", args_schema=LeadLookupSchema)
def lookup_customer_lead(lead_id: str) -> Dict[str, Any]:
    """Retrieve detailed customer lead record from CRM using a Lead ID (e.g. LEAD-501)."""
    def _execute():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            clean_id = lead_id.strip().upper()
            cursor.execute("SELECT * FROM leads WHERE lead_id = ?", (clean_id,))
            row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "found": False,
                    "message": f"Lead '{clean_id}' was not found in CRM system."
                }

            lead = dict(row)
            return {
                "success": True,
                "found": True,
                "lead_id": lead["lead_id"],
                "customer_name": lead["customer_name"],
                "company": lead["company"],
                "email": lead["email"],
                "status": lead["status"],
                "score": lead["score"],
                "assigned_to": lead["assigned_to"],
                "notes": lead["notes"],
                "created_at": lead["created_at"],
                "updated_at": lead["updated_at"]
            }

    return retry_operation(_execute)

@tool("update_lead_status", args_schema=LeadStatusUpdateSchema)
def update_lead_status(
    lead_id: str,
    new_status: str,
    notes: Optional[str] = None,
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """Change a customer lead's status in CRM (e.g., from 'new' to 'qualified'). WRITE OPERATION."""
    clean_id = lead_id.strip().upper()
    clean_status = new_status.strip().lower()

    # Idempotency check
    params = {"lead_id": clean_id, "new_status": clean_status, "notes": notes}
    cached = check_idempotency(idempotency_key, "update_lead_status", params)
    if cached:
        cached["idempotent_replay"] = True
        return cached

    def _execute():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE lead_id = ?", (clean_id,))
            row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "found": False,
                    "message": f"Lead '{clean_id}' does not exist in CRM."
                }

            old_status = row["status"]
            existing_notes = row["notes"] or ""
            updated_notes = f"{existing_notes}\n[Status changed from {old_status} to {clean_status}]: {notes or 'No notes provided.'}".strip()

            cursor.execute(
                """
                UPDATE leads 
                SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE lead_id = ?
                """,
                (clean_status, updated_notes, clean_id)
            )
            conn.commit()

            result = {
                "success": True,
                "lead_id": clean_id,
                "customer_name": row["customer_name"],
                "previous_status": old_status,
                "new_status": clean_status,
                "message": f"Lead {clean_id} status successfully updated to '{clean_status}'."
            }

            record_idempotency(idempotency_key, "update_lead_status", params, result)
            return result

    return retry_operation(_execute)

@tool("create_support_ticket", args_schema=CreateTicketSchema)
def create_support_ticket(
    title: str,
    description: str,
    customer_name: str,
    priority: str = "medium",
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new CRM support ticket with title, description, customer, and priority. WRITE OPERATION."""
    clean_priority = priority.strip().lower()
    params = {
        "title": title.strip(),
        "description": description.strip(),
        "customer_name": customer_name.strip(),
        "priority": clean_priority
    }

    # Idempotency check
    cached = check_idempotency(idempotency_key, "create_support_ticket", params)
    if cached:
        cached["idempotent_replay"] = True
        return cached

    def _execute():
        ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tickets (ticket_id, title, description, customer_name, priority, status)
                VALUES (?, ?, ?, ?, ?, 'open')
                """,
                (ticket_id, params["title"], params["description"], params["customer_name"], clean_priority)
            )
            conn.commit()

            result = {
                "success": True,
                "ticket_id": ticket_id,
                "title": params["title"],
                "customer_name": params["customer_name"],
                "priority": clean_priority,
                "status": "open",
                "message": f"Support ticket {ticket_id} created successfully."
            }

            record_idempotency(idempotency_key, "create_support_ticket", params, result)
            return result

    return retry_operation(_execute)
