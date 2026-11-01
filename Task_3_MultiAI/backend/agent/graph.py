import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from backend.agent.prompts import SYSTEM_PROMPT
from backend.config import GEMINI_API_KEY, GOOGLE_API_KEY
from backend.safety.audit import log_audit_event
from backend.safety.permissions import check_permission, requires_human_approval
from backend.tools.crm_tools import create_support_ticket, lookup_customer_lead, update_lead_status
from backend.tools.erp_tools import check_inventory, check_stock_availability

# Tool mapping
TOOLS_BY_NAME = {
    "check_inventory": check_inventory,
    "check_stock_availability": check_stock_availability,
    "lookup_customer_lead": lookup_customer_lead,
    "update_lead_status": update_lead_status,
    "create_support_ticket": create_support_ticket,
}
TOOLS_LIST = list(TOOLS_BY_NAME.values())

# Thread store for conversation memory and pending approvals
# In production, this can be backed by Redis / SQLite
SESSION_STORE: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(thread_id: str, user_role: str = "operator") -> Dict[str, Any]:
    if thread_id not in SESSION_STORE:
        SESSION_STORE[thread_id] = {
            "messages": [],
            "user_role": user_role,
            "pending_action": None,
            "created_at": datetime.utcnow().isoformat(),
        }
    return SESSION_STORE[thread_id]

def get_llm():
    """Instantiate Gemini model using available API key."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or GEMINI_API_KEY or GOOGLE_API_KEY
    if not api_key:
        return None
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key,
    ).bind_tools(TOOLS_LIST)

def parse_with_fallback(user_text: str) -> Optional[Dict[str, Any]]:
    """
    Intelligent fallback parser when Gemini API key is not configured.
    Provides complete demonstration for all 5 enterprise actions + multi-step logic.
    """
    import re
    text = user_text.lower()

    # 1. Check stock availability (e.g. "Check if 50 units of SKU-1006 are available" or "is 20 of rack available")
    if any(k in text for k in ["available", "availability", "enough stock", "can we supply", "can we fulfill"]):
        qty_match = re.search(r"(\d+)\s*(?:units?|pieces?|items?)?", text)
        requested_qty = int(qty_match.group(1)) if qty_match else 1

        sku_match = re.search(r"(SKU-\d+)", user_text, re.IGNORECASE)
        if sku_match:
            item_id = sku_match.group(1).upper()
        else:
            # Look for item name
            item_id = "Server Rack"
            for candidate in ["server rack", "transceiver", "switch", "ups", "cable", "ssd", "nvme"]:
                if candidate in text:
                    item_id = candidate
                    break

        return {
            "tool": "check_stock_availability",
            "args": {"product_identifier": item_id, "requested_quantity": requested_qty}
        }

    # 2. Check inventory (e.g. "Check inventory for SKU-1001" or "How many server racks do we have?")
    if any(k in text for k in ["inventory", "stock", "quantity", "how many", "catalog", "count"]):
        sku_match = re.search(r"(SKU-\d+)", user_text, re.IGNORECASE)
        if sku_match:
            return {"tool": "check_inventory", "args": {"product_identifier": sku_match.group(1).upper()}}

        for candidate in ["server rack", "transceiver", "switch", "ups", "cable", "ssd", "nvme"]:
            if candidate in text:
                return {"tool": "check_inventory", "args": {"product_identifier": candidate}}

        for_match = re.search(r"(?:for|of)\s+([A-Za-z0-9\- ]+)", text)
        if for_match:
            clean_item = for_match.group(1).strip().rstrip("?").replace("product", "").strip()
            return {"tool": "check_inventory", "args": {"product_identifier": clean_item}}
        return {"tool": "check_inventory", "args": {"product_identifier": "Server Rack"}}

    # 3. Update lead status (e.g. "Update lead LEAD-501 to qualified" or "change status of LEAD-502 to won")
    if "lead" in text and any(w in text for w in ["update", "change", "set", "mark", "move"]):
        lead_match = re.search(r"(LEAD-\d+)", user_text, re.IGNORECASE)
        target_status = "qualified"
        for st in ["new", "contacted", "qualified", "proposal", "won", "lost"]:
            if st in text:
                target_status = st
                break
        if lead_match:
            return {
                "tool": "update_lead_status",
                "args": {
                    "lead_id": lead_match.group(1).upper(),
                    "new_status": target_status,
                    "notes": "Updated by MultiAI assistant upon user instruction."
                }
            }

    # 4. Lookup customer lead (e.g. "Look up lead LEAD-501" or "details for LEAD-502")
    if "lead" in text or "customer" in text:
        lead_match = re.search(r"(LEAD-\d+)", user_text, re.IGNORECASE)
        if lead_match:
            return {"tool": "lookup_customer_lead", "args": {"lead_id": lead_match.group(1).upper()}}

    # 5. Create support ticket (e.g. "Create ticket for DedSec Solutions with title server offline and priority high")
    if "ticket" in text and any(w in text for w in ["create", "open", "new", "raise", "file"]):
        priority = "medium"
        for p in ["low", "medium", "high", "urgent"]:
            if p in text:
                priority = p
                break

        cust_match = re.search(r"(?:for|customer)\s+([A-Za-z0-9 ]+?)(?:\s+(?:with|priority|title|issue)|$)", text)
        customer = cust_match.group(1).strip() if cust_match else "Enterprise Customer"

        return {
            "tool": "create_support_ticket",
            "args": {
                "title": f"Enterprise Issue Reported: {user_text[:50]}...",
                "description": user_text,
                "customer_name": customer.title(),
                "priority": priority
            }
        }

    return None

def run_agent_workflow(
    thread_id: str,
    user_input: str,
    user_role: str = "operator"
) -> Dict[str, Any]:
    """
    Executes the MultiAI Agent workflow:
    1. Context & history retrieval
    2. Tool selection via Gemini (or dynamic fallback)
    3. Input & permission validation
    4. Human approval gate for write operations
    5. Execution & audit logging
    """
    session = get_or_create_session(thread_id, user_role)
    session["user_role"] = user_role
    messages = session["messages"]

    # Append user message
    messages.append(HumanMessage(content=user_input))

    llm = get_llm()
    tool_calls_to_execute = []
    agent_message = None

    if llm:
        try:
            full_prompt = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            ai_msg = llm.invoke(full_prompt)
            messages.append(ai_msg)

            if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
                for tc in ai_msg.tool_calls:
                    tool_calls_to_execute.append({
                        "id": tc.get("id"),
                        "tool": tc["name"],
                        "args": tc["args"]
                    })
            else:
                agent_message = ai_msg.content
        except Exception as e:
            # Fall back to internal parser if Gemini API call encounters issue (e.g. invalid key/network)
            parsed = parse_with_fallback(user_input)
            if parsed:
                tool_calls_to_execute.append({"id": "call_fallback", "tool": parsed["tool"], "args": parsed["args"]})
            else:
                agent_message = f"Encountered model execution error: {str(e)}"
    else:
        # Fallback parser for offline / ready testing
        parsed = parse_with_fallback(user_input)
        if parsed:
            tool_calls_to_execute.append({"id": "call_mock", "tool": parsed["tool"], "args": parsed["args"]})
        else:
            agent_message = (
                "I understood your request, but no matching ERP or CRM action was recognized. "
                "You can ask me to:\n"
                "• Check inventory (e.g. *'Check inventory for SKU-1001'* or *'Check stock for Server Rack'*)\n"
                "• Check stock availability (e.g. *'Check if 20 units of SKU-1002 are available'*)\n"
                "• Look up customer leads (e.g. *'Look up lead LEAD-501'*)\n"
                "• Update lead status (e.g. *'Update lead LEAD-501 to qualified'* — requires Human Approval)\n"
                "• Create support tickets (e.g. *'Create high priority ticket for DedSec Solutions regarding optical switch drop'* — requires Human Approval)"
            )

    execution_results = []
    pending_action = None

    for tc in tool_calls_to_execute:
        tool_name = tc["tool"]
        tool_args = tc["args"]
        call_id = tc.get("id", "call_1")

        # 1. Check Role Permission
        if not check_permission(user_role, tool_name):
            err_msg = f"Permission Denied: User role '{user_role}' is not authorized to execute '{tool_name}'."
            log_audit_event(
                thread_id=thread_id,
                action=tool_name,
                tool_name=tool_name,
                params=tool_args,
                required_approval=requires_human_approval(tool_name),
                approval_status="rejected_unauthorized",
                error=err_msg,
                user_role=user_role
            )
            messages.append(ToolMessage(content=err_msg, tool_call_id=call_id))
            execution_results.append({"tool": tool_name, "error": err_msg})
            continue

        # 2. Check Human Approval Gate for Write Operations
        if requires_human_approval(tool_name):
            pending_action = {
                "tool_name": tool_name,
                "params": tool_args,
                "description": f"Execute '{tool_name}' with parameters {json.dumps(tool_args)}",
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat(),
            }
            session["pending_action"] = pending_action

            log_audit_event(
                thread_id=thread_id,
                action=tool_name,
                tool_name=tool_name,
                params=tool_args,
                required_approval=True,
                approval_status="pending",
                user_role=user_role
            )

            approval_notice = (
                f"⏸️ **Human Approval Required**: Action `{tool_name}` is a sensitive enterprise write operation.\n\n"
                f"**Parameters:**\n```json\n{json.dumps(tool_args, indent=2)}\n```\n"
                f"Please review and **Approve** or **Reject** this operation."
            )
            messages.append(AIMessage(content=approval_notice))
            return {
                "thread_id": thread_id,
                "response": approval_notice,
                "pending_approval": pending_action,
                "executed_tools": execution_results,
            }

        # 3. Execute Read Tool
        tool_fn = TOOLS_BY_NAME.get(tool_name)
        if tool_fn:
            try:
                result = tool_fn.invoke(tool_args)
                log_audit_event(
                    thread_id=thread_id,
                    action=tool_name,
                    tool_name=tool_name,
                    params=tool_args,
                    required_approval=False,
                    approval_status="not_required",
                    result=result,
                    user_role=user_role
                )
                messages.append(ToolMessage(content=json.dumps(result), tool_call_id=call_id))
                execution_results.append({"tool": tool_name, "result": result})
            except Exception as e:
                err_str = str(e)
                log_audit_event(
                    thread_id=thread_id,
                    action=tool_name,
                    tool_name=tool_name,
                    params=tool_args,
                    required_approval=False,
                    approval_status="failed",
                    error=err_str,
                    user_role=user_role
                )
                messages.append(ToolMessage(content=f"Error: {err_str}", tool_call_id=call_id))
                execution_results.append({"tool": tool_name, "error": err_str})

    # If LLM is active and tools were executed, get synthesis response
    if llm and execution_results:
        try:
            full_prompt = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            final_ai = llm.invoke(full_prompt)
            messages.append(final_ai)
            agent_message = final_ai.content
        except Exception:
            pass

    # Build human-friendly output if agent_message is not set
    if not agent_message and execution_results:
        summaries = []
        for res in execution_results:
            t = res["tool"]
            r = res.get("result", {})
            if res.get("error"):
                summaries.append(f"❌ **{t}**: {res['error']}")
            elif t == "check_inventory":
                if r.get("found"):
                    summaries.append(
                        f"📦 **Inventory Found**: `{r['product_name']}` ({r['sku']})\n"
                        f"- **Quantity on Hand**: {r['quantity_on_hand']} units\n"
                        f"- **Unit Price**: ${r['unit_price']:,.2f}\n"
                        f"- **Location**: {r['warehouse_location']}"
                    )
                else:
                    summaries.append(f"⚠️ {r.get('message')}")
            elif t == "check_stock_availability":
                if r.get("found"):
                    status_icon = "✅" if r.get("is_available") else "⚠️"
                    summaries.append(
                        f"{status_icon} **Stock Availability**: `{r['product_name']}` ({r['sku']})\n"
                        f"- **Requested Quantity**: {r['requested_quantity']} units\n"
                        f"- **Available on Hand**: {r['quantity_on_hand']} units\n"
                        f"- **Status**: **{r['status']}** (Difference: {r['difference']:+d})\n"
                        f"- **Location**: {r['warehouse_location']}"
                    )
                else:
                    summaries.append(f"⚠️ {r.get('message', 'Product not found in ERP.')}")
            elif t == "lookup_customer_lead":
                if r.get("found"):
                    summaries.append(
                        f"👤 **Customer Lead Record**: `{r['lead_id']}`\n"
                        f"- **Customer**: {r['customer_name']} ({r['company']})\n"
                        f"- **Email**: {r['email']}\n"
                        f"- **Status**: `{r['status']}` (Score: {r['score']})\n"
                        f"- **Assigned Rep**: {r['assigned_to']}\n"
                        f"- **Notes**: {r.get('notes') or 'N/A'}"
                    )
                else:
                    summaries.append(f"⚠️ {r.get('message')}")
            else:
                summaries.append(f"✔️ **{t}**: {json.dumps(r)}")
        agent_message = "\n\n".join(summaries)

    return {
        "thread_id": thread_id,
        "response": agent_message or "Request processed.",
        "pending_approval": None,
        "executed_tools": execution_results,
    }

def process_human_approval(
    thread_id: str,
    approved: bool,
    user_role: str = "operator"
) -> Dict[str, Any]:
    """Execute or reject the pending write operation awaiting human sign-off."""
    session = get_or_create_session(thread_id, user_role)
    pending = session.get("pending_action")

    if not pending:
        return {"success": False, "message": "No pending action found for this session."}

    tool_name = pending["tool_name"]
    params = pending["params"]

    if not approved:
        session["pending_action"] = None
        log_audit_event(
            thread_id=thread_id,
            action=tool_name,
            tool_name=tool_name,
            params=params,
            required_approval=True,
            approval_status="rejected_by_human",
            user_role=user_role
        )
        msg = f"❌ Action `{tool_name}` was rejected by human operator ({user_role}). No changes were made."
        session["messages"].append(AIMessage(content=msg))
        return {"success": True, "status": "rejected", "message": msg}

    # Execute approved action
    tool_fn = TOOLS_BY_NAME.get(tool_name)
    if not tool_fn:
        return {"success": False, "message": f"Tool '{tool_name}' not found."}

    try:
        result = tool_fn.invoke(params)
        session["pending_action"] = None

        log_audit_event(
            thread_id=thread_id,
            action=tool_name,
            tool_name=tool_name,
            params=params,
            required_approval=True,
            approval_status="approved_and_executed",
            result=result,
            user_role=user_role
        )

        success_msg = f"✅ **Human Approval Granted**: Successfully executed `{tool_name}`.\n\n"
        if tool_name == "update_lead_status":
            success_msg += (
                f"- **Lead ID**: `{result.get('lead_id')}`\n"
                f"- **Customer**: {result.get('customer_name')}\n"
                f"- **Status**: `{result.get('previous_status')}` ➔ **`{result.get('new_status')}`**\n"
                f"- **Message**: {result.get('message')}"
            )
        elif tool_name == "create_support_ticket":
            success_msg += (
                f"- **Ticket ID**: `{result.get('ticket_id')}`\n"
                f"- **Title**: {result.get('title')}\n"
                f"- **Customer**: {result.get('customer_name')}\n"
                f"- **Priority**: `{result.get('priority').upper()}`\n"
                f"- **Status**: `{result.get('status')}`"
            )
        else:
            success_msg += json.dumps(result, indent=2)

        session["messages"].append(AIMessage(content=success_msg))
        return {"success": True, "status": "executed", "result": result, "message": success_msg}
    except Exception as e:
        err_msg = str(e)
        session["pending_action"] = None
        log_audit_event(
            thread_id=thread_id,
            action=tool_name,
            tool_name=tool_name,
            params=params,
            required_approval=True,
            approval_status="execution_failed",
            error=err_msg,
            user_role=user_role
        )
        fail_msg = f"⚠️ Approval granted, but execution failed: {err_msg}"
        session["messages"].append(AIMessage(content=fail_msg))
        return {"success": False, "status": "failed", "error": err_msg, "message": fail_msg}
