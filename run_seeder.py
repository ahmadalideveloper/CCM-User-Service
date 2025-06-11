# run_seeder.py
from app.core.seed import seed_route_modules_and_permissions, seed_roles

if __name__ == "__main__":
    seed_roles()
    # seed_route_modules_and_permissions()
