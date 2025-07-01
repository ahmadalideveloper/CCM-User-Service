from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModelMixin
from app.db.base_class import Base


class RouteModule(Base, BaseModelMixin):
    __tablename__ = "route_modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Add relationship to ModuleComponent
    components = relationship("ModuleComponent", back_populates="route_module")
    # NEW: Relationship for permissions directly associated with the module
    module_level_permissions = relationship("RoutePermission", 
                                            primaryjoin="and_(RouteModule.id == RoutePermission.route_module_id, RoutePermission.module_component_id.is_(None))",
                                            back_populates="route_module_for_permission")