from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from app.db.models.base import BaseModelMixin
from app.db.base_class import Base


class RouteModule(Base, BaseModelMixin):
    __tablename__ = "route_modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
