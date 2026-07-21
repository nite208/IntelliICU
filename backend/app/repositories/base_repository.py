"""
Generic Base Repository for IntelliICU.
"""

from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic CRUD repository.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, object_id: str):
        return (
            self.db.query(self.model)
            .filter(self.model.id == object_id)
            .first()
        )

    def get_all(self):
        return self.db.query(self.model).all()

    def update(self, obj: ModelType):
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType):
        self.db.delete(obj)
        self.db.commit()