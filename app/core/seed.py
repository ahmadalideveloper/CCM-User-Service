# app/core/seed.py

from app.db.session import SessionLocal
from app.db.models.route import RouteModule
from app.db.models.role import Role
from app.db.models.permission import PermissionAction
from app.db.models.route_permission import RoutePermission
from app.db.models.module_component import ModuleComponent
from app.db.models.role_permission import RolePermission
from app.db.models.user import User  # <--- Import your User model here
from app.core.security import hash_password

def seed_route_modules_and_permissions():
    db = SessionLocal()

    # Clear existing data for clean seeding (order is CRITICAL for foreign keys)
    # Delete child tables before parent tables
    db.query(RolePermission).delete()      # <--- Delete RolePermission first as it depends on RoutePermission
    db.query(RoutePermission).delete()     # <--- Then delete RoutePermission
    db.query(ModuleComponent).delete()     # <--- Then delete ModuleComponent (depends on RouteModule)
    db.query(RouteModule).delete()         # <--- Then delete RouteModule
    db.query(PermissionAction).delete()    # <--- PermissionAction can be deleted here (or earlier), as nothing else depends on it in this context.
    db.commit()

    # Define the structure including modules, components, and their actions
    # This reflects your screenshot's hierarchy
    route_structure = {
        "Facilities": {
            "actions": ["is_create", "is_read", "is_update", "is_delete", "bulk_update"],
            "components": {} # No explicit components for Facilities
        },
        "RPM": {
            "actions": ["is_create", "is_read", "is_update", "is_delete", "merge", "bulk_update"],
            "components": {} # No explicit components for RPM
        },
        "CCM": {
            "actions": [], # CCM itself might not have direct actions, only its components
            "components": {
                "Medication Review": ["is_create", "is_read", "is_update", "is_delete"],
                "Past Medical And Surgical History": ["is_create", "is_read", "is_update", "is_delete"],
                "Quick Notes": ["is_create", "is_read", "is_update", "is_delete"],
                "Insurances": ["is_create", "is_read", "is_update", "is_delete"],
                "Vitals": ["is_create", "is_read", "is_update", "is_delete"],
                "Documents": ["is_create", "is_read", "is_update", "is_delete", "merge", "share"],
                "Hospitalization": ["is_create", "is_read", "is_update", "is_delete"],
                "Medical Condition": ["is_create", "is_read", "is_update", "is_delete"],
                "Nutritionist Review": ["is_create", "is_read", "is_update", "is_delete"],
                "Other Medical Conditions": ["is_create", "is_read", "is_update", "is_delete"],
                "Allergies": ["is_create", "is_read", "is_update", "is_delete"],
                "Service Log": ["is_create", "is_read", "is_update"],
                "Survey": ["is_create", "is_read", "is_update"],
                "Progress Notes": ["is_create", "is_read", "is_update", "is_delete"],
            }
        },
        "Billing": {
            "actions": ["is_create", "is_read", "is_update", "is_delete", "merge", "bulk_update"],
            "components": {}
        },
        "COMMUNICATION": {
            "actions": [], # COMMUNICATION itself might not have direct actions
            "components": {
                "Calls": ["is_create", "is_read", "is_update", "is_delete"],
                "SMS": ["is_create", "is_read", "is_update", "is_delete"],
                "Mail": ["is_create", "is_read", "is_update", "is_delete"],
                "Message": ["is_create", "is_read", "is_update", "is_delete"],
                "Fax": ["is_create", "is_read", "is_update"],
            }
        },
        # Add other top-level modules like "Home", "Users", "Patients", "Settings"
        # from your previous seed, assuming they don't have components for now.
        "Home": {
            "actions": ["is_create", "is_read", "is_update", "is_delete"],
            "components": {}
        },
        "Users": {
            "actions": ["is_create", "is_read", "is_update", "is_delete", "is_download"],
            "components": {}
        },
        "Patients": {
            "actions": ["is_create", "is_read", "is_update", "is_delete", "bulk_upload"],
            "components": {}
        },
        "Settings": {
            "actions": ["is_read", "is_update"],
            "components": {}
        }
    }

    # First, ensure all possible PermissionActions exist
    all_action_names = set()
    for module_data in route_structure.values():
        all_action_names.update(module_data["actions"])
        for component_actions in module_data["components"].values():
            all_action_names.update(component_actions)
    
    action_objects = {}
    for action_name in all_action_names:
        action = db.query(PermissionAction).filter_by(name=action_name).first()
        if not action:
            action = PermissionAction(name=action_name, label=action_name.replace("_", " ").capitalize())
            db.add(action)
            db.commit() # Commit immediately to get ID for refresh
            db.refresh(action)
        action_objects[action_name] = action
    print("✅ Permission actions ensured.")

    # Now, process modules and components
    for module_name, module_info in route_structure.items():
        route_module = db.query(RouteModule).filter_by(name=module_name).first()
        if not route_module:
            route_module = RouteModule(name=module_name, description=f"{module_name} module")
            db.add(route_module)
            db.commit()
            db.refresh(route_module)

        # Seed Module-level Permissions
        for action_name in module_info["actions"]:
            action = action_objects[action_name]
            route_perm = db.query(RoutePermission).filter_by(
                route_module_id=route_module.id,
                action_id=action.id,
                module_component_id=None # Ensure it's a module-level permission
            ).first()
            if not route_perm:
                db.add(RoutePermission(
                    route_module_id=route_module.id,
                    action_id=action.id,
                    module_component_id=None # Explicitly set to None
                ))
        
        # Seed Components and Component-level Permissions
        for component_name, component_actions in module_info["components"].items():
            module_component = db.query(ModuleComponent).filter_by(
                name=component_name,
                route_module_id=route_module.id
            ).first()
            if not module_component:
                module_component = ModuleComponent(
                    name=component_name,
                    description=f"{component_name} component of {module_name}",
                    route_module_id=route_module.id
                )
                db.add(module_component)
                db.commit() # Commit immediately to get ID for refresh
                db.refresh(module_component)

            for action_name in component_actions:
                action = action_objects[action_name]
                route_perm = db.query(RoutePermission).filter_by(
                    module_component_id=module_component.id,
                    action_id=action.id,
                    route_module_id=None # Ensure it's a component-level permission
                ).first()
                if not route_perm:
                    db.add(RoutePermission(
                        module_component_id=module_component.id,
                        action_id=action.id,
                        route_module_id=None # Explicitly set to None
                    ))
    
    db.commit() # Final commit for all new RoutePermissions
    db.close()
    print("✅ Route modules, components, actions, and permissions seeded successfully.")


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