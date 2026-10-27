from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(
        String(10), primary_key=True
    )
    customer_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    expected_delivery: Mapped[Date | None] = mapped_column(
        Date, nullable=True
    )
