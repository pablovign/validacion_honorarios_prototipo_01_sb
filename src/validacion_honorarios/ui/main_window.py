import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.config import settings
from validacion_honorarios.db.connection import (
    check_database_connection,
)
from validacion_honorarios.ui.aduanas_view import (
    AduanasView,
)
from validacion_honorarios.ui.proveedores_view import (
    ProveedoresView,
)


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title(settings.app_name)
        self.geometry("1200x720")
        self.minsize(950, 600)

        self.current_view: ttk.Frame | None = None

        self._configure_style()
        self._build_interface()
        self._show_home()

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
            "SectionTitle.TLabel",
            font=("Sans", 16, "bold"),
        )

        style.configure(
            "Navigation.TButton",
            anchor=tk.W,
            padding=(14, 10),
        )

    def _build_interface(self) -> None:
        self.columnconfigure(
            1,
            weight=1,
        )

        self.rowconfigure(
            0,
            weight=1,
        )

        navigation = ttk.Frame(
            self,
            padding=12,
        )
        navigation.grid(
            row=0,
            column=0,
            sticky="ns",
        )

        ttk.Label(
            navigation,
            text="Validación\nde honorarios",
            style="Title.TLabel",
            justify=tk.LEFT,
        ).pack(
            fill=tk.X,
            pady=(4, 24),
        )

        ttk.Button(
            navigation,
            text="Inicio",
            command=self._show_home,
            style="Navigation.TButton",
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            navigation,
            text="Aduanas",
            command=self._show_customs_offices,
            style="Navigation.TButton",
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            navigation,
            text="Proveedores",
            command=self._show_providers,
            style="Navigation.TButton",
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            navigation,
            text="Esquemas de cotización",
            command=self._show_not_implemented,
            style="Navigation.TButton",
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            navigation,
            text="Canales de selectividad",
            command=self._show_not_implemented,
            style="Navigation.TButton",
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Separator(
            self,
            orient=tk.VERTICAL,
        ).grid(
            row=0,
            column=0,
            sticky="nse",
        )

        self.content = ttk.Frame(self)
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.content.columnconfigure(
            0,
            weight=1,
        )

        self.content.rowconfigure(
            0,
            weight=1,
        )

    def _replace_view(
        self,
        view: ttk.Frame,
    ) -> None:
        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = view

        self.current_view.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def _show_home(self) -> None:
        view = ttk.Frame(
            self.content,
            padding=28,
        )

        ttk.Label(
            view,
            text=settings.app_name,
            style="Title.TLabel",
        ).pack(
            anchor=tk.W,
            pady=(0, 12),
        )

        ttk.Label(
            view,
            text=(
                "MVP para la administración de aduanas, "
                "proveedores y esquemas de cotización."
            ),
            wraplength=700,
        ).pack(
            anchor=tk.W,
            pady=(0, 24),
        )

        database_frame = ttk.LabelFrame(
            view,
            text="Base de datos",
            padding=16,
        )
        database_frame.pack(
            fill=tk.X,
        )

        database_status = ttk.Label(
            database_frame,
            text="Conexión todavía no comprobada.",
        )
        database_status.pack(
            anchor=tk.W,
            pady=(0, 12),
        )

        def check_connection() -> None:
            database_status.configure(
                text="Comprobando conexión...",
            )
            self.update_idletasks()

            success, message = (
                check_database_connection()
            )

            if success:
                database_status.configure(
                    text=(
                        "Conexión correcta "
                        "con PostgreSQL."
                    ),
                )

                messagebox.showinfo(
                    title="Conexión correcta",
                    message=message,
                    parent=self,
                )
            else:
                database_status.configure(
                    text=(
                        "No fue posible conectar "
                        "con PostgreSQL."
                    ),
                )

                messagebox.showerror(
                    title="Error de conexión",
                    message=(
                        "No fue posible conectar "
                        "con PostgreSQL.\n\n"
                        f"Detalle:\n{message}"
                    ),
                    parent=self,
                )

        ttk.Button(
            database_frame,
            text="Comprobar conexión",
            command=check_connection,
        ).pack(
            anchor=tk.W,
        )

        ttk.Label(
            view,
            text=f"Entorno: {settings.app_env}",
        ).pack(
            side=tk.BOTTOM,
            anchor=tk.W,
            pady=(24, 0),
        )

        self._replace_view(view)

    def _show_customs_offices(self) -> None:
        view = AduanasView(
            self.content
        )

        self._replace_view(view)

    def _show_providers(self) -> None:
        view = ProveedoresView(
            self.content
        )

        self._replace_view(view)

    def _show_not_implemented(self) -> None:
        messagebox.showinfo(
            title="Próximamente",
            message=(
                "Esta sección será incorporada "
                "en los próximos pasos del MVP."
            ),
            parent=self,
        )