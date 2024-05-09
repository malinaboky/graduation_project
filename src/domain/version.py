import datetime
import uuid

from sqlalchemy import ForeignKey, UUID, VARCHAR, Boolean, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.schemas.version_schema import VersionSchema
from src.database import Base


class Version(Base):
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    is_done: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False
    )
