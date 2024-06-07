from datetime import datetime
import uuid
from flask import abort
from sqlalchemy.orm import Mapped
from flask_sqlalchemy import SQLAlchemy
from typing import NoReturn, Type, TypeVar, TypedDict

db = SQLAlchemy()

# Types
T = TypeVar("T", bound="BaseModel")

class PaginationReturn(TypedDict):
    items: list[T | None]
    total: int
    pages: int
    page: int
    per_page: int

class BaseModel(db.Model):  # type: ignore[name-defined]
    """
    BaseModel class
    Args:
        id: Random id for each table
        created_at: Represents the time each class was created
        updated_at: Represents the time each class was updated
    """

    __abstract__ = True
    id: Mapped[str] = db.Column(
        db.String(126), primary_key=True, unique=True, nullable=False
    )
    created_at: Mapped[datetime] = db.Column(db.DateTime, nullable=False)
    updated_at: Mapped[datetime] = db.Column(db.DateTime, nullable=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self) -> None:
        """
        Saves the current session into the database
        """
        self.updated_at = datetime.now()
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        """
        Deletes the current session from the database
        """
        db.session.delete(self)
        db.session.commit()

    def close(self) -> None:
        db.session.remove()

    def update(self, updates: dict) -> None:
        """
        Takes a dictionary of updates and sets the corresponding attribute
        Keyword arguments:
        updates -- A dictionary of the Model attributes you wish to update
        Return: None
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
    
    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the object.
        """
        attributes = {}
        for column in self.__table__.columns:
            attribute_name = column.name
            attribute_value = getattr(self, attribute_name)
            attributes[attribute_name] = attribute_value
        for relationship in self.__mapper__.relationships:
            related_table_name = relationship.key
            related_objects = getattr(self, related_table_name)

            if related_objects is not None:
                # If it's a one-to-one relationship, convert related object to dict
                if relationship.uselist is False:
                    attributes[related_table_name] = related_objects.to_dict()
                # If it's a one-to-many relationship, convert list of related objects to list of dicts
                else:
                    attributes[related_table_name] = [
                        obj.to_dict() for obj in related_objects
                    ]
        return attributes

    @classmethod
    def all(cls: Type[T]) -> list[T | None]:
        """
        Retrieves all objects of the current model
        """
        return cls.query.all()

    @classmethod
    def get(cls: Type[T], id: str) -> T | None:
        """
        Retrieve an object by its id or name or email or username.
        Returns the object if found, None otherwise.
        Usage:
            cls.get(name=<name>)
        """
        if id:
            return cls.query.get(id)
        return None

    @classmethod
    def get_or_404(cls: Type[T], id: str) -> T | NoReturn:
        """
        Retrieve an object by its id
        Returns the object if found, Throws a flask.abort(404) otherwise
        Usage:
            cls.get_or_404(id=<id>)
        """
        return cls.query.get(id) or abort(
            404, description="Item with given ID not found"
        )

    @classmethod
    def filter_one(cls: Type[T], **kwargs) -> T | None:
        """
        Filter the Object by the parameters supplied
        Arguments:
            **kwargs:
        Return:
            A single object if found, None otherwise
        """
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def filter_all(cls: Type[T], **kwargs) -> list[T | None]:
        """
        Filter the Object by the parameters supplied

        Arguments:
            **kwargs:
        Return:
            List of objects matching the parameters supplied, None otherwise
        """
        return cls.query.filter_by(**kwargs).all()

    @classmethod
    def filter_and_count_all(cls: Type[T], **kwargs) -> int:
        """
        Get the count of objects by the filtered parameter

        Arguments:
            **kwargs:
        Return:
            The count of objects found by query
        """
        return cls.query.filter_by(**kwargs).count()

    @classmethod
    def count_all(cls: Type[T]) -> int:
        """
        Get the count of items

        Arguments:
            **kwargs:
        Return:
            The count of objects
        """
        return len(cls.query.all())

    @classmethod
    def exists(cls: Type[T], **kwargs) -> bool:
        """
        Check if an item exists

        Arguments:
            **kwargs:
        Return:
            True if exists and False otherwise
        """
        return cls.filter_one(**kwargs) is not None

    @classmethod
    def paginate(cls: Type[T], page: int = 1, per_page: int = 10) -> PaginationReturn:
        """
        Paginate items in a model

        Arguments:
            **kwargs:
        Return:
            Dictionary of the paginated model
        """
        pagination = cls.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "per_page": pagination.per_page,
        }
