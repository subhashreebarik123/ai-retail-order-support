from sqlalchemy import select

from database import SessionLocal
from models import Order

try:
    with SessionLocal() as session:
        orders = session.scalars(select(Order)).all()

        print(f"Total orders found: {len(orders)}")

        for order in orders:
            print(
                f"Order ID: {order.order_id}, "
                f"Status: {order.status}, "
                f"Expected delivery: {order.expected_delivery}"
            )

except Exception as error:
    print("Database query failed:", type(error).__name__, str(error))
