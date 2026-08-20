import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    AdicionalCamiones,
)
from validacion_honorarios.services import (
    AdicionalCamionesService,
    ApplicationError,
)


class TramoCamionesDialog(tk.Toplevel):
    """Alta y edición de un tramo adicional de camiones."""

    def __init__(
        self,
        parent: tk.Misc,
        service: AdicionalCamionesService,
        esquema_cotizacion_id: int,
        tramo: AdicionalCamiones | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = (
            esquema_cotizacion_id
        )
        self.tramo = tramo
        self.resultado_guardado = False

        self.camion_desde_var = tk.StringVar()
        self.camion_hasta_var = tk.StringVar()

        self._configure_window()
        self._build_interface()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.wait_visibility()
        self.camion_desde_entry.focus_set()

    @property
    def is_editing(self) -> bool:
        return self.tramo is not None

    def _configure_window(self) -> None:
        self.title(
            "Editar tramo de camiones"
            if self.is_editing
            else "Nuevo tramo de camiones"
        )

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
            text="Camión desde",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        ttk.Label(
            container,
            text="Camión hasta",
        ).grid(
            row=0,
            column=1,
            sticky=tk.W,
            padx=(12, 0),
            pady=(0, 4),
        )

        self.camion_desde_entry = ttk.Entry(
            container,
            textvariable=self.camion_desde_var,
            width=18,
        )
        self.camion_desde_entry.grid(
            row=1,
            column=0,
            sticky=tk.EW,
            pady=(0, 8),
        )

        self.camion_hasta_entry = ttk.Entry(
            container,
            textvariable=self.camion_hasta_var,
            width=18,
        )
        self.camion_hasta_entry.grid(
            row=1,
            column=1,
            sticky=tk.EW,
            padx=(12, 0),
            pady=(0, 8),
        )

        ttk.Label(
            container,
            text=(
                "Los dos extremos son inclusivos. "
                "Deja «Camión hasta» vacío para indicar "
                "que el tramo no tiene límite superior."
            ),
            wraplength=430,
            foreground="#555555",
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky=tk.W,
            pady=(0, 20),
        )

        button_frame = ttk.Frame(
            container
        )
        button_frame.grid(
            row=3,
            column=0,
            columnspan=2,
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
        container.columnconfigure(
            1,
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
        if self.tramo is None:
            return

        self.camion_desde_var.set(
            str(self.tramo.camion_desde)
        )

        if self.tramo.camion_hasta is not None:
            self.camion_hasta_var.set(
                str(self.tramo.camion_hasta)
            )

    def _save(self) -> None:
        try:
            if self.tramo is None:
                self.service.crear_tramo(
                    esquema_cotizacion_id=(
                        self.esquema_cotizacion_id
                    ),
                    camion_desde=(
                        self.camion_desde_var.get()
                    ),
                    camion_hasta=(
                        self.camion_hasta_var.get()
                    ),
                )
            else:
                self.service.actualizar_tramo(
                    adicional_camiones_id=(
                        self.tramo.adicional_camiones_id
                    ),
                    camion_desde=(
                        self.camion_desde_var.get()
                    ),
                    camion_hasta=(
                        self.camion_hasta_var.get()
                    ),
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
                    "Se produjo un error inesperado "
                    "al guardar el tramo.\n\n"
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