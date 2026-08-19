from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR),
    )
from  validacion_honorarios.db.connection import (
    check_database_connection,
)

def main() -> None:
    success, message = check_database_connection()

    if success:
        print("Conexión correcta.")
        print(message)
        return

    print("Error de conexión.")
    print(message)

    raise SystemExit(1)


if __name__ == "__main__":
    main()