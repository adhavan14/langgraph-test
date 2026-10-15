from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from state import SupportState
from nodes import (
    input_guard, classify_intent, plan_and_call_model, route_after_model,
    guarded_tools, approval_gate, route_after_approval, approval_response,
    limit_reached, output_guard,
)
from guardrails import GuardrailBlocked


def build_graph():
    graph = StateGraph(SupportState)
    graph.add_node("input_guard", input_guard)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("call_model", plan_and_call_model)
    graph.add_node("guarded_tools", guarded_tools)
    graph.add_node("approval_gate", approval_gate)
    graph.add_node("approval_response", approval_response)
    graph.add_node("limit_reached", limit_reached)
    graph.add_node("output_guard", output_guard)

    graph.add_edge(START, "input_guard")
    graph.add_edge("input_guard", "classify_intent")
    graph.add_edge("classify_intent", "call_model")

    graph.add_conditional_edges(
        "call_model",
        route_after_model,
        {
            "guarded_tools": "guarded_tools",
            "approval_gate": "approval_gate",
            "output_guard": "output_guard",
            "limit_reached": "limit_reached",
        },
    )
    graph.add_edge("guarded_tools", "call_model")
    graph.add_conditional_edges(
        "approval_gate",
        route_after_approval,
        {
            "output_guard": "output_guard",
            "approval_response": "approval_response",
        },
    )
    graph.add_edge("approval_response", END)
    graph.add_edge("limit_reached", END)
    graph.add_edge("output_guard", END)
    return graph.compile(name="advanced_support_agent")


if __name__ == "__main__":
    load_dotenv()
    app = build_graph()
    while True:
        query = input("\nCustomer (or 'quit'): ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        try:
            result = app.invoke({
                "messages": [HumanMessage(content=query)],
                "audit_events": [],
            })
            print("\nAssistant:", result.get("final_answer", result["messages"][-1].content))
            print("Audit events:", result.get("audit_events", []))
        except GuardrailBlocked as exc:
            print("\nBlocked by guardrail:", exc)
