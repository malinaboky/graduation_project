import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, UUID, VARCHAR, Boolean, TIMESTAMP, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class DataPipeline(Base):

    __tablename__ = "data_pipeline"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.id", ondelete="cascade"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    pause: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    min_time_lag: Mapped[int] = mapped_column(
        INTEGER, nullable=True
    )
    type_res: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=True
    )
