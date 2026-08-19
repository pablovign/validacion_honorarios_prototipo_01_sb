import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.config import settings
from validacion_honorarios.db.connection import (
    check_database_connection,
)


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title(settings.app_name)
        self.geometry("1000x650")
        self.minsize(800, 500)

        self._configure_style()
        self._build_interface()

    def _configure_style(self) -> None:
        style = ttk.Style(self)

        available_themes = style.theme_names()

        if "clam" in available_themes:
            style.theme_use("clam")

        style.configure(
            "Title.TLabel",
            font=("Sans", 18, "bold"),
        )

        style.configure(
            "Status.TLabel",
            font=("Sans", 10),
        )

        style.configure(
            "Accent.TButton",
            padding=(12, 6),
        )

    def _build_interface(self) -> None:
        main_frame = ttk.Frame(
            self,
            padding=24,
        )
        main_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        title = ttk.Label(
            main_frame,
            text=settings.app_name,
            style="Title.TLabel",
        )
        title.pack(
            anchor=tk.W,
            pady=(0, 12),
        )

        description = ttk.Label(
            main_frame,
            text=(
                "MVP para la administración de aduanas, "
                "proveedores y esquemas de cotización."
            ),
            wraplength=700,
        )
        description.pack(
            anchor=tk.W,
            pady=(0, 24),
        )

        database_frame = ttk.LabelFrame(
            main_frame,
            text="Base de datos",
            padding=16,
        )
        database_frame.pack(
            fill=tk.X,
        )

        self.database_status = ttk.Label(
            database_frame,
            text="Conexión todavía no comprobada.",
            style="Status.TLabel",
        )
        self.database_status.pack(
            anchor=tk.W,
            pady=(0, 12),
        )

        check_button = ttk.Button(
            database_frame,
            text="Comprobar conexión",
            command=self._check_connection,
            style="Accent.TButton",
        )
        check_button.pack(
            anchor=tk.W,
        )

        footer = ttk.Label(
            main_frame,
            text=f"Entorno: {settings.app_env}",
        )
        footer.pack(
            side=tk.BOTTOM,
            anchor=tk.W,
            pady=(24, 0),
        )

    def _check_connection(self) -> None:
        self.database_status.configure(
            text="Comprobando conexión...",
        )
        self.update_idletasks()

        success, message = check_database_connection()

        if success:
            self.database_status.configure(
                text="Conexión correcta con PostgreSQL.",
            )

            messagebox.showinfo(
                title="Conexión correcta",
                message=message,
                parent=self,
            )
        else:
            self.database_status.configure(
                text="No fue posible conectar con PostgreSQL.",
            )

            messagebox.showerror(
                title="Error de conexión",
                message=(
                    "No fue posible conectar con PostgreSQL.\n\n"
                    f"Detalle:\n{message}"
                ),
                parent=self,
            )