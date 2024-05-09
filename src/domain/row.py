import uuid

from sqlalchemy import Integer, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Row(Base):
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("version.id", ondelete="cascade"), nullable=False, index=True
    )
    number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
