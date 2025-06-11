# app/core/seed.py

from app.db.session import SessionLocal
from app.db.models.route import RouteModule
from app.db.models.role import Role
from app.db.models.permission import PermissionAction
from app.db.models.route_permission import RoutePermission

def seed_route_modules_and_permissions():
    db = SessionLocal()

    route_data = {
        "Home": ["is_create", "is_read", "is_update", "is_delete"],
        "Users": ["is_create", "is_read", "is_update", "is_delete", "is_download"],
        "Patients": ["is_create", "is_read", "is_update", "is_delete", "bulk_upload"],
        "CCM": ["is_create", "is_read", "is_update", "is_delete", "merge"],
        "Settings": ["is_read", "is_update"]
    }

    for module_name, actions in route_data.items():
        # 1. Create or fetch RouteModule
        route_module = db.query(RouteModule).filter_by(name=module_name).first()
        if not route_module:
            route_module = RouteModule(name=module_name, description=f"{module_name} module")
            db.add(route_module)
            db.commit()
            db.refresh(route_module)

        for action_name in actions:
            # 2. Create or fetch PermissionAction
            action = db.query(PermissionAction).filter_by(name=action_name).first()
            if not action:
                action = PermissionAction(name=action_name, label=action_name.replace("_", " ").capitalize())
                db.add(action)
                db.commit()
                db.refresh(action)

            # 3. Create RoutePermission if not exists
            route_perm = db.query(RoutePermission).filter_by(
                route_module_id=route_module.id,
                action_id=action.id
            ).first()

            if not route_perm:
                route_perm = RoutePermission(
                    route_module_id=route_module.id,
                    action_id=action.id
                )
                db.add(route_perm)

    db.commit()
    db.close()
    print("✅ Route modules, actions, and permissions seeded successfully.")


def seed_roles():
    db = SessionLocal()
    roles_to_seed = [
        {"name": "Admin", "description": "Administrator with full access"},
        {"name": "Care Coordinator", "description": "Manages patient care workflows"},
        {"name": "Nurse", "description": "Handles daily patient health monitoring"},
        {"name": "Doctor", "description": "Reviews and advises on patient care"},
    ]

    for role_data in roles_to_seed:
        existing = db.query(Role).filter_by(name=role_data["name"]).first()
        if not existing:
            db.add(Role(**role_data))
    
    db.commit()
    print("✅ Roles seeded successfully.")    