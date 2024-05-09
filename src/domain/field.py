import uuid

from sqlalchemy import UUID, ForeignKey, VARCHAR, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Field(Base):
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    type: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    column_number: Mapped[int] = mapped_column(
        Integer, nullable=True
    )
