from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session,joinedload
from app.db.session import get_db
from app.db.models.route import RouteModule
from app.db.models.route_permission import RoutePermission
from app.db.models.role import Role,RolePermission
from app.db.models.module_component import ModuleComponent
from app.schemas.response import SuccessResponse, ErrorResponse
router = APIRouter()


@router.get("/summary", response_model=SuccessResponse, summary="Get summary of all routes and permissions with role assignments")
async def get_route_summary_with_role(
    role_id: int = Query(..., description="ID of the role to fetch permissions for"),
    db: Session = Depends(get_db)
):
    """
    Fetches a comprehensive summary of all available modules and their permissions,
    including components, indicating for each permission whether it is currently
    assigned to the specified role. This correctly accounts for soft-deleted assignments.
    """
    # Eager load relationships to prevent N+1 queries
    role = db.query(Role).options(
        joinedload(Role.role_permissions).joinedload(RolePermission.route_permission)
                                        .joinedload(RoutePermission.action),
        joinedload(Role.role_permissions).joinedload(RolePermission.route_permission)
                                        .joinedload(RoutePermission.route_module_for_permission),
        joinedload(Role.role_permissions).joinedload(RolePermission.route_permission)
                                        .joinedload(RoutePermission.module_component_for_permission)
    ).filter(Role.id == role_id, Role.is_removed == False).first() # Filter active roles
    
    if not role:
        raise HTTPException(status_code=404, detail=ErrorResponse(
            message="Active role not found", error_code="ROLE_NOT_FOUND"
        ).model_dump())

    # Build a set of ONLY the ACTIVE route_permission_ids assigned to this role.
    assigned_permission_ids = {
        rp.route_permission_id
        for rp in role.role_permissions
        if not rp.is_removed
    }

    # Eager load all modules, their components, and all associated permissions
    route_modules = db.query(RouteModule).options(
        joinedload(RouteModule.module_level_permissions).joinedload(RoutePermission.action),
        joinedload(RouteModule.components).joinedload(ModuleComponent.component_permissions).joinedload(RoutePermission.action)
    ).filter(RouteModule.is_removed == False).all() # Filter active modules

    response_data = []

    for module in route_modules:
        module_data = {
            "module_id": module.id,
            "module_name": module.name,
            "actions": [], # For module-level actions
            "components": [] # For nested components
        }

        # 1. Add Module-level Actions
        for route_perm in module.module_level_permissions:
            if not route_perm.is_removed: # Ensure the route_permission itself is not soft-deleted
                module_data["actions"].append({
                    "action_id": route_perm.action.id,
                    "action_name": route_perm.action.name,
                    "action_label": route_perm.action.label,
                    "route_permission_id": route_perm.id,
                    "is_assigned": route_perm.id in assigned_permission_ids
                })
        
        # 2. Add Components and their Actions
        for component in module.components:
            if not component.is_removed: # Filter active components
                component_data = {
                    "component_id": component.id,
                    "component_name": component.name,
                    "actions": []
                }
                for route_perm in component.component_permissions:
                    if not route_perm.is_removed: # Ensure the route_permission itself is not soft-deleted
                        component_data["actions"].append({
                            "action_id": route_perm.action.id,
                            "action_name": route_perm.action.name,
                            "action_label": route_perm.action.label,
                            "route_permission_id": route_perm.id,
                            "is_assigned": route_perm.id in assigned_permission_ids
                        })
                module_data["components"].append(component_data)

        response_data.append(module_data)

    return SuccessResponse(
        message=f"Route summary with role assignments for role '{role.name}' fetched successfully",
        data=response_data
    )