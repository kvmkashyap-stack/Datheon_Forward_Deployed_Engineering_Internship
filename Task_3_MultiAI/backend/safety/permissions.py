from typing import Set

# Actions categorized by side effects
READ_ACTIONS: Set[str] = {
    "check_inventory",
    "check_stock_availability",
    "lookup_customer_lead",
    "list_all_leads",
    "list_all_tickets",
}

# Operations that mutate business state
WRITE_ACTIONS: Set[str] = {
    "update_lead_status",
    "create_support_ticket",
    "adjust_inventory_quantity",
}

# Actions that mandate human approval before execution
APPROVAL_REQUIRED_ACTIONS: Set[str] = {
    "update_lead_status",
    "create_support_ticket",
}

ROLE_PERMISSIONS = {
    "viewer": READ_ACTIONS,
    "operator": READ_ACTIONS | WRITE_ACTIONS,
    "admin": READ_ACTIONS | WRITE_ACTIONS,
}

def is_write_action(action_name: str) -> bool:
    """Check if an action modifies enterprise data."""
    return action_name in WRITE_ACTIONS

def requires_human_approval(action_name: str) -> bool:
    """Check if an action must be approved by a human operator."""
    return action_name in APPROVAL_REQUIRED_ACTIONS

def check_permission(user_role: str, action_name: str) -> bool:
    """Verify if user role has authorization to execute action."""
    allowed = ROLE_PERMISSIONS.get(user_role.lower(), set())
    return action_name in allowed
