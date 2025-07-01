# db/models/route_permission.py

from sqlalchemy import Column, Integer, String, Boolean,ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModelMixin
from app.db.base_class import Base
from app.db.models.route import RouteModule
from app.db.models.permission import PermissionAction
from app.db.models.module_component import ModuleComponent
# from app.db.models.role_permission import RolePermission


class RoutePermission(Base, BaseModelMixin):
    __tablename__ = "route_permissions"

    id = Column(Integer, primary_key=True, index=True)
    route_module_id = Column(Integer, ForeignKey("route_modules.id"))
    module_component_id = Column(Integer, ForeignKey("module_components.id"), nullable=True)
    action_id = Column(Integer, ForeignKey("permission_actions.id"))

    # route_module = relationship("RouteModule", backref="permissions")
    action = relationship("PermissionAction")

    # NEW: These are the relationships that the API is looking for
    route_module_for_permission = relationship("RouteModule", 
                                               primaryjoin="and_(RouteModule.id == RoutePermission.route_module_id, RoutePermission.module_component_id.is_(None))",
                                               back_populates="module_level_permissions")
    module_component_for_permission = relationship("ModuleComponent", 
                                                    primaryjoin="and_(ModuleComponent.id == RoutePermission.module_component_id, RoutePermission.route_module_id.is_(None))",
                                                    back_populates="component_permissions")

    __table_args__ = (
        UniqueConstraint('route_module_id', 'action_id', name='_module_action_uc'),
        UniqueConstraint('module_component_id', 'action_id', name='_component_action_uc'),
    )
