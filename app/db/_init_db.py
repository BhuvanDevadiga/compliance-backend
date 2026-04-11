import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.exc import OperationalError


MAX_ATTEMPTS = 30
RETRY_DELAY_SECONDS = 2
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_alembic_upgrade() -> None:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(config, "head")


def main() -> None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            run_alembic_upgrade()
            return
        except OperationalError:
            if attempt == MAX_ATTEMPTS:
                raise
            print(
                f"Database not ready yet; retrying migrations "
                f"({attempt}/{MAX_ATTEMPTS})..."
            )
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    main()
