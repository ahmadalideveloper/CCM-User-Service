# app/schemas/role.py

from pydantic import BaseModel
from typing import Optional

class RoleCreateSchema(BaseModel):
    name: str

class RoleResponseSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True 



class PermissionAssignment(BaseModel):
    permission_id: int
    is_read: Optional[bool] = False
    is_create: Optional[bool] = False
    is_update: Optional[bool] = False
    is_delete: Optional[bool] = False
    is_allow_ccm: Optional[bool] = False


class RolePermissionAssignRequest(BaseModel):
    role_id: int
    permissions: list[PermissionAssignment]