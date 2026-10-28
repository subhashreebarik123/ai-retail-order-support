
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from database import SessionLocal
from models import Order
from rag import search_policies
from langchain_service import generate_policy_answer


class SupportState(TypedDict, total=False):
    question: str
    order_id: str
    policy_context: str
    answer: str
    route: str


def route_question(state: SupportState) -> str:
    """Choose the order or policy workflow."""
    match = re.search(
        r"\bORD\d{4}\b",
        state["question"],
        re.IGNORECASE,
    )

    return "order" if match else "policy"


def order_lookup_node(state: SupportState) -> dict:
    """Retrieve an order from MySQL."""
    order_id = re.search(
        r"\bORD\d{4}\b",
        state["question"],
        re.IGNORECASE,
    ).group().upper()

    with SessionLocal() as session:
        order = session.get(Order, order_id)

        if order is None:
            return {
                "answer": (
                    f"Sorry, I could not find order {order_id}. "
                    "Please check the order ID."
                ),
                "route": "order",
            }

        delivery = (
            order.expected_delivery.isoformat()
            if order.expected_delivery
            else ""
        )

        return {
            "answer": (
                f"Order ID: {order.order_id}. "
                f"Status: {order.status}. "
                f"Estimated delivery: {delivery}."
            ),
            "route": "order",
        }


def policy_answer_node(state: SupportState) -> dict:
    """Retrieve policy context and generate a LangChain answer."""
    chunks = search_policies(state["question"], n_results=2)
    policy_context = "\n\n".join(chunks)

    answer = generate_policy_answer(
        question=state["question"],
        policy_context=policy_context,
    )

    return {
        "policy_context": policy_context,
        "answer": answer,
        "route": "policy",
    }


def build_support_graph():
    """Build and compile the retail support workflow."""
    graph = StateGraph(SupportState)

    graph.add_node("order_lookup", order_lookup_node)
    graph.add_node("policy_answer", policy_answer_node)

    graph.add_conditional_edges(
        START,
        route_question,
        {
            "order": "order_lookup",
            "policy": "policy_answer",
        },
    )

    graph.add_edge("order_lookup", END)
    graph.add_edge("policy_answer", END)

    return graph.compile()


support_graph = build_support_graph()