from redis import Redis
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.core.settings import Settings
from app.models import User
from app.repositories import users

# Verified against when the email is unknown, so response time doesn't reveal which emails exist.
_DUMMY_HASH = hash_password("not-a-real-password")


def authenticate(db: Session, redis: Redis, settings: Settings, email: str, password: str) -> User:
    key = f"login_attempts:{email.strip().lower()}"
    if int(redis.get(key) or 0) >= settings.login_max_attempts:
        raise AppError("RATE_LIMITED", "Too many login attempts, try again later.", 429)

    user = users.get_by_email(db, email.strip())
    ok = verify_password(user.password_hash if user else _DUMMY_HASH, password)
    if user is None or not ok:
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, settings.login_window_s)
        pipe.execute()
        raise AppError("INVALID_CREDENTIALS", "Invalid email or password.", 401)

    redis.delete(key)
    return user


def ensure_admin(db: Session, settings: Settings) -> bool:
    """Create the ADMIN_EMAIL/ADMIN_PASSWORD user if absent. Returns True if created."""
    if not settings.admin_email or not settings.admin_password:
        return False
    if users.get_by_email(db, settings.admin_email):
        return False
    users.create(
        db,
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password.get_secret_value()),
        display_name="Admin",
    )
    db.commit()
    return True
