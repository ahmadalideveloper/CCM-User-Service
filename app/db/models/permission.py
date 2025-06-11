# db/models/permission.py
from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from app.db.models.base import BaseModelMixin
from app.db.base_class import Base


class PermissionAction(Base, BaseModelMixin):
    __tablename__ = "permission_actions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., 'read', 'merge'
    label = Column(String(50), nullable=True)               # display label if needed
