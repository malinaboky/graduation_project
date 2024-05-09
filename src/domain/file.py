import uuid

from sqlalchemy import ForeignKey, UUID, VARCHAR, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class File(Base):
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    path: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    type: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
