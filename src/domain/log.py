import uuid
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, VARCHAR, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Log(Base):
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        VARCHAR(length=50), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False
    )
    message: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=True
    )
