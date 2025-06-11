# db/models/user_permission.py
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModelMixin
from app.db.base_class import Base
from app.db.models.route_permission import RoutePermission

class UserPermission(Base, BaseModelMixin):
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_permission_id = Column(Integer, ForeignKey("route_permissions.id"))

    route_permission = relationship("RoutePermission")