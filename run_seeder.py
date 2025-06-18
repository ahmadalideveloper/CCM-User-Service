# run_seeder.py
from app.core.seed import seed_route_modules_and_permissions, seed_roles,seed_users

if __name__ == "__main__":
    # seed_roles()
    seed_users()
    # seed_route_modules_and_permissions()
