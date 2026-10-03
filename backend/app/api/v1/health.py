from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import DbSession
from app.core.redis import get_redis
from app.schemas.health import Liveness, Readiness

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def liveness() -> Liveness:
    return Liveness(status="ok")


@router.get("/ready", response_model=Readiness, responses={503: {"model": Readiness}})
def readiness(db: DbSession) -> JSONResponse:
    checks: dict[str, str] = {}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
    try:
        get_redis().ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"
    healthy = all(v == "ok" for v in checks.values())
    body = {"status": "ok" if healthy else "degraded", "checks": checks}
    return JSONResponse(status_code=200 if healthy else 503, content=body)
