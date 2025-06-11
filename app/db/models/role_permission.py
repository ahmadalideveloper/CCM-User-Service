# db/models/role_permission.py
from sqlalchemy import Column, Integer, ForeignKey, Boolean,UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModelMixin
from app.db.base_class import Base
from app.db.models.route_permission import RoutePermission


# class RolePermission(Base, BaseModelMixin):
#     __tablename__ = "role_permissions"

#     id = Column(Integer, primary_key=True, index=True)
#     role_id = Column(Integer, ForeignKey("roles.id"))
#     route_permission_id = Column(Integer, ForeignKey("route_permissions.id"))

#     role = relationship("Role", back_populates="permissions")
    # route_permission = relationship("RoutePermission", back_populates="role_permissions")


class RolePermission(Base, BaseModelMixin):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    route_permission_id = Column(Integer, ForeignKey("route_permissions.id"), nullable=False)

    # Relationships to access the related Role and RoutePermission objects
    role = relationship("Role", backref="role_permissions")
    route_permission = relationship("RoutePermission")

    # Ensures that a specific role-permission assignment can only exist once
    __table_args__ = (
        UniqueConstraint('role_id', 'route_permission_id', name='_role_route_permission_uc'),
    )    