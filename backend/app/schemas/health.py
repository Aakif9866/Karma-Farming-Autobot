from typing import Literal

from pydantic import BaseModel


class Liveness(BaseModel):
    status: Literal["ok"]


class Readiness(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, Literal["ok", "error"]]
