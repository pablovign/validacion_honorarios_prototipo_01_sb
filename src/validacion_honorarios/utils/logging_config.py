import logging

from validacion_honorarios.config import PROJECT_ROOT, settings


def configure_logging() -> None:
    logs_dir = PROJECT_ROOT / "logs"

    logs_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file = logs_dir / "application.log"

    logging.basicConfig(
        level=getattr(
            logging,
            settings.log_level,
            logging.INFO,
        ),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )