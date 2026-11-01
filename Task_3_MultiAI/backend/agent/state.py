from typing import Annotated, Dict, Any, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class PendingAction(TypedDict):
    tool_name: str
    params: Dict[str, Any]
    description: str
    status: str  # "pending", "approved", "rejected"
    requested_at: str

class MultiAIState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    thread_id: str
    user_role: str  # "viewer", "operator", "admin"
    pending_action: Optional[PendingAction]
    audit_trail: List[Dict[str, Any]]
