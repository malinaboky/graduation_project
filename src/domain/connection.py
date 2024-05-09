import uuid

from sqlalchemy import ForeignKey, UUID, VARCHAR, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Connection(Base):
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    connect_str: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    db_type: Mapped[str] = mapped_column(
        VARCHAR(length=50), nullable=False
    )
    db_name: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=True
    )
    schema: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=True
    )
    table: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    auth: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    user: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(
        VARCHAR(length=512), nullable=True
    )
