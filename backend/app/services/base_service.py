"""
Generic Base Service for IntelliICU.
"""

from typing import Generic, TypeVar

from app.repositories.base_repository import BaseRepository

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Generic business service.
    """

    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def get_by_id(self, object_id: str):
        return self.repository.get_by_id(object_id)

    def get_all(self):
        return self.repository.get_all()

    def create(self, obj: ModelType):
        return self.repository.create(obj)

    def update(self, obj: ModelType):
        return self.repository.update(obj)

    def delete(self, obj: ModelType):
        return self.repository.delete(obj)