from datetime import datetime
import uuid
from flask import abort
from sqlalchemy.orm import Mapped
from flask_sqlalchemy import SQLAlchemy
from typing import Any

db = SQLAlchemy()


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
    def all(cls):
        """
        Retrieves all objects of the current model
        """
        return cls.query.all()

    @classmethod
    def get(cls, id: str):
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
    def get_or_404(cls, id: str):
        """
        Retrieve an object by its id
        Returns the object if found, None otherwise.
        Usage:
            cls.get(id=<id>)
        """
        if id:
            return cls.query.get(id) or abort(
                404, description="Item with given ID not found"
            )
        return None