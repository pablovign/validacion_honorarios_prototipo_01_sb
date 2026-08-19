import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    Aduana,
    Proveedor,
)
from validacion_honorarios.services import (
    ApplicationError,
    ProveedorService,
)


class ProveedorDialog(tk.Toplevel):
    """Ventana modal para crear o modificar un proveedor."""

    def __init__(
        self,
        parent: tk.Misc,
        service: ProveedorService,
        proveedor: Proveedor | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.proveedor = proveedor
        self.aduanas = service.listar_aduanas()
        self.aduana_por_descripcion: dict[str, Aduana] = {}

        self.resultado_guardado = False

        self.razon_social_var = tk.StringVar()
        self.cuit_var = tk.StringVar()
        self.aduana_var = tk.StringVar()

        self._configure_window()
        self._build_interface()
        self._load_customs_offices()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.wait_visibility()
        self.razon_social_entry.focus_set()

    @property
    def is_editing(self) -> bool:
        return self.proveedor is not None

    def _configure_window(self) -> None:
        title = (
            "Editar proveedor"
            if self.is_editing
            else "Nuevo proveedor"
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
            text="Razón social",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.razon_social_entry = ttk.Entry(
            container,
            textvariable=self.razon_social_var,
            width=48,
        )
        self.razon_social_entry.grid(
            row=1,
            column=0,
            sticky=tk.EW,
            pady=(0, 14),
        )

        ttk.Label(
            container,
            text="CUIT",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.cuit_entry = ttk.Entry(
            container,
            textvariable=self.cuit_var,
            width=24,
        )
        self.cuit_entry.grid(
            row=3,
            column=0,
            sticky=tk.EW,
            pady=(0, 14),
        )

        ttk.Label(
            container,
            text="Aduana",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.aduana_combobox = ttk.Combobox(
            container,
            textvariable=self.aduana_var,
            state="readonly",
            width=46,
        )
        self.aduana_combobox.grid(
            row=5,
            column=0,
            sticky=tk.EW,
            pady=(0, 20),
        )

        button_frame = ttk.Frame(container)
        button_frame.grid(
            row=6,
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

    def _load_customs_offices(self) -> None:
        descriptions: list[str] = []

        for aduana in self.aduanas:
            description = (
                f"{aduana.codigo} - {aduana.nombre}"
            )

            descriptions.append(description)
            self.aduana_por_descripcion[description] = aduana

        self.aduana_combobox.configure(
            values=descriptions,
        )

        if descriptions and not self.is_editing:
            self.aduana_var.set(
                descriptions[0]
            )

    def _load_initial_values(self) -> None:
        if self.proveedor is None:
            return

        self.razon_social_var.set(
            self.proveedor.razon_social
        )

        self.cuit_var.set(
            self.proveedor.cuit
        )

        description = (
            f"{self.proveedor.aduana.codigo} - "
            f"{self.proveedor.aduana.nombre}"
        )

        self.aduana_var.set(description)

    def _selected_customs_office_id(
        self,
    ) -> int | None:
        description = self.aduana_var.get()

        aduana = self.aduana_por_descripcion.get(
            description
        )

        if aduana is None:
            messagebox.showwarning(
                title="Aduana obligatoria",
                message=(
                    "Selecciona una aduana "
                    "para el proveedor."
                ),
                parent=self,
            )
            return None

        return aduana.aduana_id

    def _save(self) -> None:
        aduana_id = (
            self._selected_customs_office_id()
        )

        if aduana_id is None:
            return

        try:
            if self.proveedor is None:
                self.service.crear(
                    aduana_id=aduana_id,
                    razon_social=(
                        self.razon_social_var.get()
                    ),
                    cuit=self.cuit_var.get(),
                )
            else:
                self.service.actualizar(
                    proveedor_id=(
                        self.proveedor.proveedor_id
                    ),
                    aduana_id=aduana_id,
                    razon_social=(
                        self.razon_social_var.get()
                    ),
                    cuit=self.cuit_var.get(),
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
                    "al guardar el proveedor.\n\n"
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