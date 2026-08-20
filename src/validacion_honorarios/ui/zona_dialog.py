import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import Zona
from validacion_honorarios.services import (
    ApplicationError,
    ZonaTarifaService,
)


class ZonaDialog(tk.Toplevel):
    """Ventana modal para crear o modificar una zona."""

    def __init__(
        self,
        parent: tk.Misc,
        service: ZonaTarifaService,
        esquema_cotizacion_id: int,
        zona: Zona | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = (
            esquema_cotizacion_id
        )
        self.zona = zona

        self.resultado_guardado = False
        self.nombre_var = tk.StringVar()

        self._configure_window()
        self._build_interface()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.wait_visibility()
        self.nombre_entry.focus_set()

    @property
    def is_editing(self) -> bool:
        return self.zona is not None

    def _configure_window(self) -> None:
        title = (
            "Editar zona"
            if self.is_editing
            else "Nueva zona"
        )

        self.title(title)
        self.resizable(False, False)

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

    def _build_interface(self) -> None:
        container = ttk.Frame(
            self,
            padding=20,
        )
        container.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        ttk.Label(
            container,
            text="Nombre de la zona",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.nombre_entry = ttk.Entry(
            container,
            textvariable=self.nombre_var,
            width=42,
        )
        self.nombre_entry.grid(
            row=1,
            column=0,
            sticky=tk.EW,
            pady=(0, 12),
        )

        ttk.Label(
            container,
            text=(
                "Si el proveedor no diferencia zonas, "
                "puedes utilizar GENERAL."
            ),
            foreground="#555555",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(0, 20),
        )

        button_frame = ttk.Frame(container)
        button_frame.grid(
            row=3,
            column=0,
            sticky=tk.E,
        )

        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancel,
        ).pack(
            side=tk.LEFT,
            padx=(0, 8),
        )

        ttk.Button(
            button_frame,
            text="Guardar",
            command=self._save,
        ).pack(
            side=tk.LEFT,
        )

        container.columnconfigure(
            0,
            weight=1,
        )

        self.bind(
            "<Return>",
            lambda _event: self._save(),
        )

        self.bind(
            "<Escape>",
            lambda _event: self._cancel(),
        )

    def _load_initial_values(self) -> None:
        if self.zona is None:
            return

        self.nombre_var.set(
            self.zona.nombre
        )

    def _save(self) -> None:
        try:
            if self.zona is None:
                self.service.crear_zona(
                    esquema_cotizacion_id=(
                        self.esquema_cotizacion_id
                    ),
                    nombre=self.nombre_var.get(),
                )
            else:
                self.service.actualizar_zona(
                    zona_id=self.zona.zona_id,
                    nombre=self.nombre_var.get(),
                )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo guardar",
                message=str(exc),
                parent=self,
            )
            return

        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=(
                    "Se produjo un error al guardar "
                    "la zona.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self.resultado_guardado = True
        self.destroy()

    def _cancel(self) -> None:
        self.resultado_guardado = False
        self.destroy()