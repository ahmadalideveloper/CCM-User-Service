from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.response import ErrorResponse

from app.api.v1.endpoints import auth,user,role,route


app = FastAPI(
    title="User Management Microservice",
    description="This service handles user registration, login, and management.",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            data=exc.errors()
        ).dict()
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "status" in exc.detail:
        # Already in structured ErrorResponse format
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            error_code="HTTP_ERROR"
        ).dict()
    )


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(role.router, prefix="/api/v1/role", tags=["Role"])
app.include_router(route.router, prefix="/api/v1/route", tags=["Route"])



