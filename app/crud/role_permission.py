# app/crud/role_permission.py

from sqlalchemy.orm import Session
from app.db.models.role_permission import RolePermission

def assign_permissions_to_role(db: Session, role_id: int, permissions: list[dict]):
    # Optional: clear old permissions
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()

    role_permissions = []
    for perm in permissions:
        role_permissions.append(
            RolePermission(
                role_id=role_id,
                permission_id=perm["permission_id"],
                is_read=perm.get("is_read", False),
                is_create=perm.get("is_create", False),
                is_update=perm.get("is_update", False),
                is_delete=perm.get("is_delete", False),
                is_allow_ccm=perm.get("is_allow_ccm", False)
            )
        )

    db.add_all(role_permissions)
    db.commit()
    return {"message": "Permissions with flags assigned to role."}
