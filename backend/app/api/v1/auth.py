from fastapi import APIRouter, Request

from app.api.deps import CurrentUser, DbSession
from app.core.redis import get_redis
from app.core.settings import get_settings
from app.schemas.auth import LoginRequest, UserOut
from app.services import auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginRequest, request: Request, db: DbSession) -> UserOut:
    user = auth.authenticate(db, get_redis(), get_settings(), body.email, body.password)
    request.session.clear()
    request.session["uid"] = str(user.id)
    return UserOut.model_validate(user)


@router.post("/logout", status_code=204)
def logout(request: Request) -> None:
    request.session.clear()


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
