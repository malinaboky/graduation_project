import datetime
import uuid

from sqlalchemy import ForeignKey, UUID, VARCHAR, Boolean, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class RunningJob(Base):
    __tablename__ = "running_job"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("data_pipeline.id", ondelete="cascade"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("job.id", ondelete="cascade"), nullable=False, index=True
    )

