from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, text

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    phone_number = Column(String(), nullable=True)
    admin = Column(Boolean, server_default="False", nullable=False)
