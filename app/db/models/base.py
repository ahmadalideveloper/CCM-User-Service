# app/db/models/base.py

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, Integer, Boolean

class BaseModelMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now())

    @declared_attr
    def removed_at(cls):
        return Column(DateTime, nullable=True)

    @declared_attr
    def created_by(cls):
        return Column(Integer, nullable=True)

    @declared_attr
    def updated_by(cls):
        return Column(Integer, nullable=True)

    @declared_attr
    def removed_by(cls):
        return Column(Integer, nullable=True)

    @declared_attr
    def is_removed(cls):
        return Column(Boolean, default=False)
