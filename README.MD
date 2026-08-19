# Validación de honorarios

Aplicación de escritorio para administrar proveedores despachantes
de aduana y sus esquemas de cotización.

## Tecnologías

- Python
- Tkinter
- PostgreSQL
- SQLAlchemy
- Alembic

## Paquetes del sistema en Debian 13

```bash
sudo apt install python3 python3-venv python3-pip python3-tk
```

## Preparación

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Crear `.env` a partir de `.env.example`.

## Comprobar PostgreSQL

```bash
python scripts/check_database.py
```

## Ejecutar la aplicación

```bash
python main.py
```