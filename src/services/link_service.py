import uuid

from src.domain.link import Link
from src.schemas.enums.link_type import LinkType
from src.schemas.link_schema import LinkSchemaAdd
from src.repositories.repository import AbstractRepository


class LinkService:
    def __init__(self, link_repo: AbstractRepository):
        self.link_repo: AbstractRepository = link_repo()

    async def create_link(self, pipeline_id, link: str, type: str) -> uuid.UUID:
        link = LinkSchemaAdd(
            pipeline_id=pipeline_id,
            link=link,
            type=LinkType[type].name
        )
        return await self.link_repo.add_one(link.model_dump())

    async def get_pipeline_link(self, pipeline_id) -> Link:
        link = await self.link_repo.find_one(pipeline_id)
        return link
