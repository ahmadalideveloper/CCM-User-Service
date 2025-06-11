from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.route import RouteModule
from app.db.models.role import Role
from app.schemas.response import SuccessResponse, ErrorResponse

router = APIRouter()


@router.get("/summary", response_model=SuccessResponse)
async def get_route_summary_with_role(
    role_id: int = Query(..., description="ID of the role to fetch permissions for"),
    db: Session = Depends(get_db)
):
    """
    Fetches a comprehensive summary of all available modules and their permissions,
    indicating for each permission whether it is currently assigned to the specified role.
    This correctly accounts for soft-deleted assignments.
    """
    role = db.query(Role).filter_by(id=role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=ErrorResponse(
            message="Role not found", error_code="ROLE_NOT_FOUND"
        ).model_dump())

    # --- CRITICAL FIX HERE ---
    # Build a set of ONLY the ACTIVE route_permission_ids assigned to this role.
    assigned_permission_ids = {
        rp.route_permission_id
        for rp in role.role_permissions # Assuming 'role_permissions' is the correct relationship name
        if not rp.is_removed # Filter out soft-deleted assignments
    }
    # --- END CRITICAL FIX ---

    route_modules = db.query(RouteModule).all()
    response_data = []

    for module in route_modules:
        module_data = {
            "module_id": module.id,
            "module_name": module.name,
            "actions": []
        }

        # Iterate through all possible RoutePermissions for this module
        for route_perm in module.permissions: # `module.permissions` refers to RoutePermission objects
            module_data["actions"].append({
                "action_id": route_perm.action.id,
                "action_name": route_perm.action.name,
                "action_label": route_perm.action.label,
                "route_permission_id": route_perm.id,
                # Check if this route_permission_id is in our *active* assigned set
                "is_assigned": route_perm.id in assigned_permission_ids
            })

        response_data.append(module_data)

    return SuccessResponse(
        message=f"Route summary with role assignments for role '{role.name}' fetched successfully",
        data=response_data
    )
