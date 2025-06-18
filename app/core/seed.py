# app/core/seed.py

from app.db.session import SessionLocal
from app.db.models.route import RouteModule
from app.db.models.role import Role
from app.db.models.permission import PermissionAction
from app.db.models.route_permission import RoutePermission
from app.db.models.user import User  # <--- Import your User model here
from app.core.security import hash_password

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


def seed_users():
    db = SessionLocal()

    # Get roles to assign to users
    admin_role = db.query(Role).filter_by(name="Admin").first()
    care_coordinator_role = db.query(Role).filter_by(name="Care Coordinator").first()
    # Ensure roles exist before trying to use their IDs
    if not admin_role or not care_coordinator_role:
        print("Skipping user seeding: Admin or Care Coordinator roles not found. Please seed roles first.")
        db.close()
        return

    print("seed Users")
    users_to_seed = [
        {
            "email": "admin@example.com",
            "username":"admin@example.com",
            "password": "Password123!", # This will be hashed
            "first_name": "Admin",
            "last_name": "User",
            "phone_number":"+13313302540",
            "role_id": admin_role.id
        },
        {
            "email": "cc@example.com",
            "username":"cc@example.com",
            "password": "Password123!", # This will be hashed
            "first_name": "Care",
            "last_name": "Coordinator",
            "phone_number":"+13313302541",
            "role_id": care_coordinator_role.id
        },
        {
            "email": "test@example.com",
            "username":"test@example.com",
            "password": "TestPassword", # This will be hashed
            "first_name": "Test",
            "last_name": "User",
            "role_id": admin_role.id, # Example: another admin user
            "phone_number":"+13313302542", 
            "is_removed": True # Example of a soft-deleted user
        }
    ]

    for user_data in users_to_seed:
        existing_user = db.query(User).filter_by(email=user_data["email"]).first()
        if not existing_user:
            print(f"Before hass_password")
            hashed_password = hash_password(user_data["password"])
            
            user = User(
                email=user_data["email"],
                username = user_data['username'],
                password=hashed_password, # Store the hashed password
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone_number=user_data['phone_number'],
                role_id=user_data["role_id"],
                is_removed=user_data.get("is_removed", False) # Handle optional is_removed
            )
            db.add(user)
        else:
            print(f"User with email {user_data['email']} already exists. Skipping.")

    db.commit()
    db.close()
    print("✅ Users seeded successfully.")    