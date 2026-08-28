from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


def get_database_url() -> str:
    """Build PostgreSQL connection URL from environment variables."""

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise ValueError(
            f"Environment variable belum lengkap: {missing_variables}"
        )

    return (
        f"postgresql+psycopg://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )


def get_engine() -> Engine:
    """Create SQLAlchemy engine."""

    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )


def test_connection() -> None:
    """Test PostgreSQL connection."""

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), version();")
        )

        database_name, version = result.fetchone()

        print("Database connection: SUCCESS")
        print(f"Database: {database_name}")
        print(f"PostgreSQL: {version}")


if __name__ == "__main__":
    test_connection()