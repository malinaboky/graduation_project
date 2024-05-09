import uuid
from typing import Any, Optional

from sqlalchemy import UUID, ForeignKey, VARCHAR, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Job(Base):
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    field_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("field.id", ondelete="cascade"), default=None, nullable=True, index=True
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("version.id", ondelete='SET NULL'), nullable=True, index=True
    )
    order: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    type: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    params: Mapped[dict[str, Any]] = mapped_column(nullable=True)

