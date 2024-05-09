import datetime
import uuid

from sqlalchemy import ForeignKey, UUID, VARCHAR, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Data(Base):
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("field.id", ondelete="cascade"), nullable=False, index=True
    )
    row_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("row.id", ondelete="cascade"), nullable=False, index=True
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("version.id", ondelete="cascade"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    last_job: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

