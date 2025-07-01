# app/db/models/module_component.py (New file)
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModelMixin # Assuming BaseModelMixin and Base are in base.py
from app.db.base_class import Base

class ModuleComponent(Base, BaseModelMixin):
    __tablename__ = "module_components"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    route_module_id = Column(Integer, ForeignKey("route_modules.id"), nullable=False)

    # Relationships
    route_module = relationship("RouteModule", back_populates="components")
     # NEW: Relationship for permissions specific to this component
    component_permissions = relationship("RoutePermission", 
                                         primaryjoin="and_(ModuleComponent.id == RoutePermission.module_component_id, RoutePermission.route_module_id.is_(None))",
                                         back_populates="module_component_for_permission")