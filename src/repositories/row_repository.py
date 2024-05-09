from src.domain.row import Row
from src.repositories.repository import SQLAlchemyRepository


class RowRepository(SQLAlchemyRepository):
    model = Row
