import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Path
from google import genai
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from models import Order

load_dotenv()

app = FastAPI(
    title="AI Retail Order Support Assistant",
    description="Backend API for retail customer support",
    version="1.0.0",
)

# Gemini configuration
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# API response models
class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    status: str
    estimated_delivery: str


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


def find_order(order_id: str):
    """Retrieve an order from MySQL."""
    with SessionLocal() as session:
        return session.get(Order, order_id)


def format_order_response(order: Order) -> dict:
    """Convert a database order into the existing API format."""
    return {
        "order_id": order.order_id,
        "customer_name": order.customer_name,
        "status": order.status,
        "estimated_delivery": (
            order.expected_delivery.isoformat()
            if order.expected_delivery
            else ""
        ),
    }


@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Retail Order Support Assistant!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-retail-order-support",
    }


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str = Path(
        ...,
        min_length=7,
        max_length=7,
        pattern=r"^ORD\d{4}$",
        description="Order ID such as ORD1001",
    )
):
    try:
        order = find_order(order_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Unable to access the order database. Please try again.",
        )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order {order_id} not found",
        )

    return format_order_response(order)


@app.post("/chat", response_model=ChatResponse)
def chat_with_gemini(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    # Check whether the question contains an order ID.
    order_match = re.search(
        r"\bORD\d{4}\b",
        question,
        re.IGNORECASE,
    )

    if order_match:
        order_id = order_match.group().upper()

        try:
            order = find_order(order_id)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=503,
                detail="Unable to access the order database. Please try again.",
            )

        if order is None:
            return ChatResponse(
                answer=(
                    f"Sorry, I could not find order {order_id}. "
                    "Please check the order ID."
                )
            )

        order_data = format_order_response(order)

        return ChatResponse(
            answer=(
                f"Order ID: {order_data['order_id']}. "
                f"Status: {order_data['status']}. "
                f"Estimated delivery: "
                f"{order_data['estimated_delivery']}."
            )
        )

    # Use Gemini for general customer support questions.
    try:
        response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=(
        "You are a friendly and professional retail customer support assistant. "
        "Answer questions about orders, delivery, returns, refunds, and product support. "
        "Give clear, practical, step-by-step guidance when useful. "
        "Never invent order status, delivery dates, refund status, or company policies. "
        "If specific order information is needed, ask the customer for their order ID. "
        "If a policy depends on the retailer, explain that the customer should check "
        "the retailer's official policy. "
        "Keep your answer concise and easy to understand.\n\n"
        f"Customer question: {question}"
    ),
    config={"http_options": {"timeout": 60000}}

        )

        if not response.text:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response.",
            )

        return ChatResponse(answer=response.text)

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Gemini error type: {type(exc).__name__}")
        print(f"Gemini error details: {exc}")

        raise HTTPException(
            status_code=502,
            detail="Unable to get a response from Gemini. Please try again.",
        )
