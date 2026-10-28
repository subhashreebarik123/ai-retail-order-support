from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from models import Order
from rag import ensure_knowledge_base
from workflow import support_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the retail policy knowledge base on startup."""
    ensure_knowledge_base()
    yield


app = FastAPI(
    title="AI Retail Order Support Assistant",
    description="Backend API for retail customer support",
    version="1.0.0",
    lifespan=lifespan,
)


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
    """Convert an order into the API response format."""
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
    """Get order details from MySQL."""
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
def chat_with_assistant(request: ChatRequest):
    """Use LangGraph to route order and policy questions."""
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    try:
        result = support_graph.invoke({"question": question})

        answer = result.get("answer", "")

        if not answer or not answer.strip():
            raise HTTPException(
                status_code=502,
                detail="The assistant returned an empty response.",
            )

        return ChatResponse(answer=answer.strip())

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Unable to access the order database. Please try again.",
        )

    except ValueError as exc:
        if "API key is not configured" in str(exc):
            raise HTTPException(
                status_code=503,
                detail="Gemini API key is not configured.",
            )

        print(f"Assistant error type: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate an answer. Please try again.",
        )

    except Exception as exc:
        print(f"Assistant error type: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Unable to process your question. Please try again.",
        )
