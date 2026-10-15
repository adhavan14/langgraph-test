from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


Intent = Literal["order_status", "refund", "policy", "account", "general"]


class SupportState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    intent: Intent
    order_id: str
    customer_id: str
    order_data: dict
    refund_eligibility: dict
    policy_text: str
    account_summary: dict
    next_action: str
    risk_level: Literal["low", "medium", "high"]
    approval_required: bool
    approval_status: Literal["pending", "approved", "rejected", "not_required"]
    final_answer: str
    blocked_reason: str
    audit_events: list[dict]
    tool_calls_count: int
    max_tool_calls: int
