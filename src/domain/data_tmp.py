import uuid

from sqlalchemy import UUID, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class DataTMP(Base):

    __tablename__ = "data_tmp"

    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("version.id", ondelete="cascade"), nullable=False, index=True
    )
    data_id: Mapped[uuid.UUID] = mapped_column(
        UUID, nullable=False
    )
    value: Mapped[str] = mapped_column(
        VARCHAR(length=255), nullable=False
    )

