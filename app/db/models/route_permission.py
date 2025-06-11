# db/models/route_permission.py

from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModelMixin
from app.db.base_class import Base
from app.db.models.route import RouteModule
from app.db.models.permission import PermissionAction
# from app.db.models.role_permission import RolePermission


class RoutePermission(Base, BaseModelMixin):
    __tablename__ = "route_permissions"

    id = Column(Integer, primary_key=True, index=True)
    route_module_id = Column(Integer, ForeignKey("route_modules.id"))
    action_id = Column(Integer, ForeignKey("permission_actions.id"))

    route_module = relationship("RouteModule", backref="permissions")
    action = relationship("PermissionAction")
    # role_permissions = relationship("RolePermission", back_populates="route_permission", cascade="all, delete-orphan")
