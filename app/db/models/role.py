# app/db/models/role.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModelMixin
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.role_permission import RolePermission

class Role(Base, BaseModelMixin):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    description = Column(String(255), nullable=True)
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


