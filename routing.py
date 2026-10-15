from typing import Literal
from state import SupportState


def route_by_intent(state: SupportState) -> Literal["order_flow", "refund_flow", "policy_flow", "account_flow", "general_flow"]:
    intent = state.get("intent", "general")
    if intent == "order_status":
        return "order_flow"
    if intent == "refund":
        return "refund_flow"
    if intent == "policy":
        return "policy_flow"
    if intent == "account":
        return "account_flow"
    return "general_flow"
