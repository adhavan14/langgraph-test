import re
from langchain_core.messages import HumanMessage


class GuardrailBlocked(Exception):
    pass


INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior) instructions",
    r"reveal (the )?(system prompt|secrets|api key)",
    r"bypass (all )?guardrails",
    r"act as (the )?system",
]


def audit_event(state: dict, event_type: str, detail: str) -> dict:
    events = list(state.get("audit_events", []))
    events.append({"type": event_type, "detail": detail})
    return {"audit_events": events}


def check_user_input(text: str) -> None:
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS):
        raise GuardrailBlocked("Potential prompt injection detected.")


def validate_tool_call(tool_name: str, args: dict, state: dict) -> None:
    allowed = {"lookup_order", "check_refund_eligibility", "lookup_customer", "search_policy"}
    if tool_name not in allowed:
        raise GuardrailBlocked(f"Tool not allowed: {tool_name}")

    if tool_name in {"lookup_order", "check_refund_eligibility"}:
        order_id = str(args.get("order_id", "")).upper()
        if not re.fullmatch(r"ORD-\d{4}", order_id):
            raise GuardrailBlocked("Invalid order ID format.")
        if state.get("order_id") and order_id != state["order_id"]:
            raise GuardrailBlocked("Tool order ID does not match the order in the request.")

    if tool_name == "lookup_customer":
        customer_id = str(args.get("customer_id", "")).upper()
        if not re.fullmatch(r"CUST-\d{3}", customer_id):
            raise GuardrailBlocked("Invalid customer ID format.")

    if tool_name == "search_policy":
        topic = str(args.get("topic", "")).lower()
        if not any(word in topic for word in ("refund", "shipping", "account")):
            raise GuardrailBlocked("Policy topic is not allowlisted.")


def assess_risk(text: str, intent: str) -> tuple[str, bool]:
    """Demo policy: high-value refunds require human approval."""
    amount_match = re.search(r"(?:\$|usd\s*)(\d+(?:\.\d{1,2})?)", text.lower())
    mentions_refund = intent == "refund" or "refund" in text.lower()
    if mentions_refund and amount_match and float(amount_match.group(1)) >= 200:
        return "high", True
    if mentions_refund:
        return "medium", False
    return "low", False


def check_output(text: str) -> None:
    if re.search(r"(?i)\bapi[_ -]?key\s*[:=]", text):
        raise GuardrailBlocked("Possible secret detected in output.")
