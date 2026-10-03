import uuid
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import AppError
from app.models import User
from app.repositories import users

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(request: Request, db: DbSession) -> User:
    raw = request.session.get("uid")
    user = users.get_by_id(db, uuid.UUID(raw)) if raw else None
    if user is None:
        request.session.clear()
        raise AppError("UNAUTHENTICATED", "Login required.", 401)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
