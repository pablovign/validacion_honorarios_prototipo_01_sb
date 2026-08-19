import logging

from validacion_honorarios.ui.main_window import MainWindow
from validacion_honorarios.utils.logging_config import (
    configure_logging,
)


logger = logging.getLogger(__name__)


def run() -> None:
    configure_logging()

    logger.info(
        "Iniciando la aplicación Validación de honorarios."
    )

    app = MainWindow()
    app.mainloop()

    logger.info(
        "Aplicación finalizada."
    )