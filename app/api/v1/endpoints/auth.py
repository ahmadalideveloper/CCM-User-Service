from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.response import SuccessResponse, ErrorResponse
from app.schemas.auth import LoginRequestSchema
from app.constants import response_constants as rc
from app.services.auth_service import authenticate_user
from app.db.session import get_db
from starlette.status import HTTP_401_UNAUTHORIZED
from app.exceptions.api_exception import APIException
from app.core.security import create_access_token
from starlette.concurrency import run_in_threadpool




router = APIRouter()

@router.post("/login", response_model=SuccessResponse, responses={
    401: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
})
async def login(payload: LoginRequestSchema,db: Session = Depends(get_db)):
    user = await run_in_threadpool(authenticate_user, db, payload.username, payload.password)
    if not user:
        raise APIException(
            message=rc.ERROR_INVALID_CREDENTIALS,
            error_code=rc.AUTH_FAILED,
            status_code=HTTP_401_UNAUTHORIZED
        )

    access_token = create_access_token(user.id,user.role.id)
    
    return SuccessResponse(
        message=rc.SUCCESS_LOGIN,
        data={"access_token": access_token, "token_type": "bearer"}
    )

