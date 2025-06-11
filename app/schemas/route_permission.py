from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Re-using existing ActionPermissionRequest and ModulePermissionRequest
# (These remain the same as in previous responses)
class ActionPermissionRequest(BaseModel):
    action_id: int
    action_name: str
    action_label: str
    route_permission_id: int
    is_assigned: bool

class ModulePermissionRequest(BaseModel):
    module_id: int
    module_name: str
    actions: List[ActionPermissionRequest]

# --- NEW: Request Model for the API Endpoint ---
class UpdateRolePermissionsRequest(BaseModel):
    role_id: int # Now included in the payload
    permissions: List[ModulePermissionRequest]

