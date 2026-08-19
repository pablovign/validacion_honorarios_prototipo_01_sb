from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import URL


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def require_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"La variable de entorno obligatoria "
            f"'{name}' no está configurada."
        )

    return value.strip()


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    documents_dir: Path

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


def load_settings() -> Settings:
    documents_path = PROJECT_ROOT / os.getenv(
        "DOCUMENTS_DIR",
        "data/documentos",
    )

    documents_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        db_port = int(os.getenv("DB_PORT", "5432"))
    except ValueError as exc:
        raise RuntimeError(
            "DB_PORT debe ser un número entero."
        ) from exc

    return Settings(
        app_name=os.getenv(
            "APP_NAME",
            "Validación de honorarios",
        ),
        app_env=os.getenv(
            "APP_ENV",
            "development",
        ),
        log_level=os.getenv(
            "LOG_LEVEL",
            "INFO",
        ).upper(),
        db_host=require_env("DB_HOST"),
        db_port=db_port,
        db_name=require_env("DB_NAME"),
        db_user=require_env("DB_USER"),
        db_password=require_env("DB_PASSWORD"),
        documents_dir=documents_path,
    )


settings = load_settings()