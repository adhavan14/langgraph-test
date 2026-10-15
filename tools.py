from langchain_core.tools import tool

# Fake data only. Replace with authenticated service calls in real applications.
ORDERS = {
    "ORD-1001": {"status": "shipped", "days_since_delivery": 2, "amount": 89.99, "customer_id": "CUST-101"},
    "ORD-1002": {"status": "delivered", "days_since_delivery": 18, "amount": 249.00, "customer_id": "CUST-202"},
    "ORD-1003": {"status": "delivered", "days_since_delivery": 42, "amount": 129.00, "customer_id": "CUST-101"},
}
CUSTOMERS = {
    "CUST-101": {"tier": "gold", "masked_email": "a***@example.com"},
    "CUST-202": {"tier": "standard", "masked_email": "b***@example.com"},
}
POLICIES = {
    "refund": "Demo policy: eligible items can be returned within 30 days of delivery, subject to item condition.",
    "shipping": "Demo policy: delivery estimates depend on carrier and service level.",
    "account": "Demo policy: verify the customer's identity before disclosing account-specific information.",
}


@tool
def lookup_order(order_id: str) -> dict:
    """Look up an order by ID, such as ORD-1001."""
    return ORDERS.get(order_id.upper(), {"error": "Order not found"})


@tool
def check_refund_eligibility(order_id: str) -> dict:
    """Check whether an order falls within the demo 30-day refund window."""
    order = ORDERS.get(order_id.upper())
    if not order:
        return {"eligible": False, "reason": "Order not found"}
    days = order["days_since_delivery"]
    return {
        "eligible": days <= 30,
        "days_since_delivery": days,
        "amount": order["amount"],
        "reason": "Within demo window" if days <= 30 else "Outside demo window",
    }


@tool
def lookup_customer(customer_id: str) -> dict:
    """Return a limited, masked customer profile by customer ID."""
    return CUSTOMERS.get(customer_id.upper(), {"error": "Customer not found"})


@tool
def search_policy(topic: str) -> str:
    """Search demo policies for refund, shipping, or account topics."""
    topic = topic.lower()
    for key, value in POLICIES.items():
        if key in topic:
            return value
    return "No matching demo policy found."
