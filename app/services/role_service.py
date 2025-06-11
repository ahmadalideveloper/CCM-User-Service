# app/services/role_service.py

from sqlalchemy.orm import Session
from app.db.models.role import Role
from app.schemas.role import RoleCreateSchema
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any, Optional
from app.db.models.role_permission import RolePermission


def create_role(db: Session, role_in: RoleCreateSchema) -> Role:
    new_role = Role(name=role_in.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


def assign_or_update_role_permissions_from_api(
    db_session: Session,
    role_id: int, # role_id is now explicitly passed here
    permissions_data: List[Dict[str, Any]], # This is now the 'permissions' list from the payload
    user_id_performing_action: Optional[int] = None
):
    """
    Assigns or updates module permissions for a given role based on the API response structure,
    using soft deletion. The role_id is now passed as a direct argument.
    """
    try:
        role = db_session.query(Role).filter(Role.id == role_id, Role.is_removed == False).first()
        print(f"role_id ={role_id}")
        if not role:
            raise ValueError(f"Active Role with ID {role_id} not found.")

        existing_role_permissions_map = {
            rp.route_permission_id: rp
            for rp in db_session.query(RolePermission)
                                .filter(RolePermission.role_id == role_id)
                                .all()
        }
        
        active_existing_route_permission_ids = {
            rp.route_permission_id
            for rp in existing_role_permissions_map.values()
            if not rp.is_removed
        }

        desired_active_route_permission_ids = set()
        for module_data in permissions_data: # permissions_data is now the list of modules
            for action_data in module_data.get("actions", []):
                route_permission_id = action_data.get("route_permission_id")
                is_assigned = action_data.get("is_assigned")

                if route_permission_id is None:
                    print(f"Warning: Missing 'route_permission_id' for an action. Skipping.")
                    continue
                
                if is_assigned:
                    desired_active_route_permission_ids.add(route_permission_id)

        to_activate_or_create_ids = desired_active_route_permission_ids - active_existing_route_permission_ids
        to_deactivate_ids = active_existing_route_permission_ids - desired_active_route_permission_ids

        for rp_id in to_activate_or_create_ids:
            existing_rp_entry = existing_role_permissions_map.get(rp_id)
            if existing_rp_entry:
                if existing_rp_entry.is_removed:
                    existing_rp_entry.is_removed = False
                    existing_rp_entry.removed_at = None
                    existing_rp_entry.removed_by = None
                    existing_rp_entry.updated_at = func.now()
                    existing_rp_entry.updated_by = user_id_performing_action
                    db_session.add(existing_rp_entry)
            else:
                new_role_permission = RolePermission(
                    role_id=role_id,
                    route_permission_id=rp_id,
                    is_removed=False,
                    created_by=user_id_performing_action,
                    updated_by=user_id_performing_action
                )
                db_session.add(new_role_permission)

        for rp_id in to_deactivate_ids:
            rp_to_deactivate = existing_role_permissions_map.get(rp_id)
            if rp_to_deactivate and not rp_to_deactivate.is_removed:
                rp_to_deactivate.is_removed = True
                rp_to_deactivate.removed_at = func.now()
                rp_to_deactivate.removed_by = user_id_performing_action
                rp_to_deactivate.updated_at = func.now()
                rp_to_deactivate.updated_by = user_id_performing_action
                db_session.add(rp_to_deactivate)

        db_session.commit()

    except IntegrityError as e:
        db_session.rollback()
        raise ValueError(f"Database integrity error during permission update: {e}") from e
    except Exception as e:
        db_session.rollback()
        raise e