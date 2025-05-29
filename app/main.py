from fastapi import FastAPI
from app.api.v1.endpoints import auth,user


app = FastAPI(
    title="User Management Microservice",
    description="This service handles user registration, login, and management.",
    version="1.0.0"
)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])

