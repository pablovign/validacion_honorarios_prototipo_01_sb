from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from validacion_honorarios.config import settings


engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

SessionFactory = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionFactory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connection() -> tuple[bool, str]:
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()

            postgresql_version = connection.execute(
                text("SELECT version()")
            ).scalar_one()

        message = (
            f"Conexión correcta a '{database_name}'.\n"
            f"{postgresql_version}"
        )

        return True, message

    except Exception as exc:
        return False, str(exc)