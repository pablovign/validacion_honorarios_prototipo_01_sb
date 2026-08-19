import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import Aduana
from validacion_honorarios.services import (
    AduanaService,
    ApplicationError,
)


class AduanaDialog(tk.Toplevel):
    """Ventana modal para crear o modificar una aduana."""

    def __init__(
        self,
        parent: tk.Misc,
        service: AduanaService,
        aduana: Aduana | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.aduana = aduana
        self.resultado_guardado = False

        self.codigo_var = tk.StringVar()
        self.nombre_var = tk.StringVar()

        self._configure_window()
        self._build_interface()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.wait_visibility()
        self.codigo_entry.focus_set()

    @property
    def is_editing(self) -> bool:
        return self.aduana is not None

    def _configure_window(self) -> None:
        title = (
            "Editar aduana"
            if self.is_editing
            else "Nueva aduana"
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
            text="Código",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.codigo_entry = ttk.Entry(
            container,
            textvariable=self.codigo_var,
            width=12,
        )
        self.codigo_entry.grid(
            row=1,
            column=0,
            sticky=tk.EW,
            pady=(0, 14),
        )

        ttk.Label(
            container,
            text="Nombre",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.nombre_entry = ttk.Entry(
            container,
            textvariable=self.nombre_var,
            width=45,
        )
        self.nombre_entry.grid(
            row=3,
            column=0,
            sticky=tk.EW,
            pady=(0, 20),
        )

        button_frame = ttk.Frame(container)
        button_frame.grid(
            row=4,
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
        if self.aduana is None:
            return

        self.codigo_var.set(
            self.aduana.codigo
        )

        self.nombre_var.set(
            self.aduana.nombre
        )

    def _save(self) -> None:
        codigo = self.codigo_var.get()
        nombre = self.nombre_var.get()

        try:
            if self.aduana is None:
                self.service.crear(
                    codigo=codigo,
                    nombre=nombre,
                )
            else:
                self.service.actualizar(
                    aduana_id=self.aduana.aduana_id,
                    codigo=codigo,
                    nombre=nombre,
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
                    "al guardar la aduana.\n\n"
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