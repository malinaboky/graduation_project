from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, VARCHAR
from sqlalchemy.orm import mapped_column, Mapped

from src.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    email: Mapped[str] = mapped_column(
        VARCHAR(length=255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        VARCHAR(length=512), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

