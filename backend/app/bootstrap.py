"""One-off startup tasks run by the `migrate` container after `alembic upgrade head`."""

import structlog

from app.core.db import get_sessionmaker
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.services.auth import ensure_admin


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, json=settings.app_env != "local")
    with get_sessionmaker()() as db:
        created = ensure_admin(db, settings)
    structlog.get_logger().info("bootstrap.admin", created=created)


if __name__ == "__main__":
    main()
