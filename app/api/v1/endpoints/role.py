# app/api/routes/role.py

from fastapi import APIRouter, Depends, HTTPException,Query,status
from sqlalchemy.orm import Session
from app.schemas.role import RoleCreateSchema, RoleResponseSchema,RolePermissionAssignRequest
from app.schemas.route_permission import UpdateRolePermissionsRequest
from app.schemas.response import SuccessResponse,ErrorResponse
from app.db.models.role import Role
from app.services.role_service import create_role,assign_or_update_role_permissions_from_api
from app.crud.role_permission import assign_permissions_to_role
from app.db.session import get_db
from typing import List, Dict, Any, Optional
from app.services.role_service import assign_or_update_role_permissions_from_api

router = APIRouter()

@router.post("/", response_model=RoleResponseSchema)
def create_new_role(role_in: RoleCreateSchema, db: Session = Depends(get_db)):
    return create_role(db, role_in)

@router.get("/permissions", response_model=SuccessResponse, summary="Get assigned modules and permissions for a role")
async def get_assigned_routes(
    role_id: int = Query(..., description="ID of the role to fetch permissions for"),
    db: Session = Depends(get_db)
):
    """
    Fetches all modules and their associated permissions that are currently assigned
    to a specific role.
    
    Returns the data in a structured format, grouped by module, showing only
    the explicitly assigned (non-soft-deleted) permissions.
    """
    role = db.query(Role).filter_by(id=role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=ErrorResponse(
            message="Role not found", error_code="ROLE_NOT_FOUND"
        ).model_dump())

    modules_data_map: Dict[int, Dict[str, Any]] = {}

    # USE role.role_permissions HERE
    for role_perm in role.role_permissions:
        if not role_perm.is_removed:
            route_perm = role_perm.route_permission
            module = route_perm.route_module
            action = route_perm.action

            if module.id not in modules_data_map:
                modules_data_map[module.id] = {
                    "module_id": module.id,
                    "module_name": module.name,
                    "actions": []
                }
            
            modules_data_map[module.id]["actions"].append({
                "action_id": action.id,
                "action_name": action.name,
                "action_label": action.label,
                "route_permission_id": route_perm.id,
                "is_assigned": True
            })
    
    result = list(modules_data_map.values())

    return SuccessResponse(
        message=f"Assigned permissions for role '{role.name}' fetched successfully",
        data=result
    )





@router.post(
    "/update_permissions", # Changed path: no {role_id} in URL
    response_model=SuccessResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Role Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Assign or update modules and permissions for a role"
)
async def update_role_permissions(
    request: UpdateRolePermissionsRequest, # Now expects the new combined request model
    db: Session = Depends(get_db), # Replace with your actual get_db
    # Example: current_user: User = Depends(get_current_active_user)
):
    """
    This endpoint allows you to assign or update the modules and permissions
    for a specific role, utilizing soft deletion. The role ID is provided
    within the request body.
    """
    try:
        user_id = 1 # Replace with actual user ID from authentication context

        # Extract role_id and permissions data from the request body
        role_id = request.role_id
        permissions_data = [p.model_dump() for p in request.permissions] # Convert Pydantic list to list of dicts
        print(f"In API role_id = {role_id}")
        assign_or_update_role_permissions_from_api(db, role_id, permissions_data, user_id)
        
        return SuccessResponse(message=f"Permissions for role {role_id} updated successfully.")
    
    except ValueError as e:
        if "Role with ID" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    message=str(e),
                    error_code="ROLE_NOT_FOUND"
                ).model_dump()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    message=f"Invalid request data: {e}",
                    error_code="BAD_REQUEST"
                ).model_dump()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                message=f"An unexpected error occurred while updating permissions: {e}",
                error_code="INTERNAL_SERVER_ERROR"
            ).model_dump()
        )
    