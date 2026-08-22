import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    EsquemaCotizacion,
    Proveedor,
)
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
)


class EsquemaCotizacionDialog(tk.Toplevel):
    """Alta y edición de la cabecera de un esquema."""

    def __init__(
        self,
        parent: tk.Misc,
        service: EsquemaCotizacionService,
        esquema: EsquemaCotizacion | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema = esquema
        self.proveedores = service.listar_proveedores()

        self.proveedor_por_descripcion: dict[
            str,
            Proveedor,
        ] = {}

        self.resultado_guardado = False

        self.esquema_guardado_id: int | None = None

        self.proveedor_var = tk.StringVar()
        self.aduana_var = tk.StringVar()
        self.fecha_inicio_var = tk.StringVar()
        self.moneda_var = tk.StringVar(
            value="ARS"
        )

        self._configure_window()
        self._build_interface()
        self._load_providers()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.wait_visibility()
        self.proveedor_combobox.focus_set()

    @property
    def is_editing(self) -> bool:
        return self.esquema is not None

    def _configure_window(self) -> None:
        title = (
            "Editar esquema de cotización"
            if self.is_editing
            else "Nuevo esquema de cotización"
        )

        self.title(title)
        self.geometry("620x510")
        self.minsize(560, 470)
        self.resizable(True, True)

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

    def _build_interface(self) -> None:
        container = ttk.Frame(
            self,
            padding=20,
        )
        container.pack(
            fill=tk.BOTH,
            expand=True,
        )

        ttk.Label(
            container,
            text="Proveedor",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.proveedor_combobox = ttk.Combobox(
            container,
            textvariable=self.proveedor_var,
            state="readonly",
            width=58,
        )
        self.proveedor_combobox.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(0, 14),
        )

        self.proveedor_combobox.bind(
            "<<ComboboxSelected>>",
            self._provider_selected,
        )

        ttk.Label(
            container,
            text="Aduana asociada",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.aduana_entry = ttk.Entry(
            container,
            textvariable=self.aduana_var,
            state="readonly",
        )
        self.aduana_entry.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(0, 14),
        )

        ttk.Label(
            container,
            text="Fecha de inicio",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        ttk.Label(
            container,
            text="Moneda",
        ).grid(
            row=4,
            column=1,
            sticky=tk.W,
            padx=(12, 0),
            pady=(0, 4),
        )

        self.fecha_inicio_entry = ttk.Entry(
            container,
            textvariable=self.fecha_inicio_var,
            width=22,
        )
        self.fecha_inicio_entry.grid(
            row=5,
            column=0,
            sticky=tk.EW,
            pady=(0, 4),
        )

        self.moneda_combobox = ttk.Combobox(
            container,
            textvariable=self.moneda_var,
            state="readonly",
            values=(
                "ARS",
                "USD",
            ),
            width=18,
        )
        self.moneda_combobox.grid(
            row=5,
            column=1,
            sticky=tk.EW,
            padx=(12, 0),
            pady=(0, 4),
        )

        ttk.Label(
            container,
            text="Formato: DD/MM/AAAA",
            foreground="#555555",
        ).grid(
            row=6,
            column=0,
            sticky=tk.W,
            pady=(0, 14),
        )

        ttk.Label(
            container,
            text="Observaciones",
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.observaciones_text = tk.Text(
            container,
            height=8,
            width=60,
            wrap=tk.WORD,
        )
        self.observaciones_text.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(0, 20),
        )

        text_scrollbar = ttk.Scrollbar(
            container,
            orient=tk.VERTICAL,
            command=self.observaciones_text.yview,
        )
        text_scrollbar.grid(
            row=8,
            column=2,
            sticky="ns",
            pady=(0, 20),
        )

        self.observaciones_text.configure(
            yscrollcommand=text_scrollbar.set,
        )

        button_frame = ttk.Frame(container)
        button_frame.grid(
            row=9,
            column=0,
            columnspan=3,
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
            text="Guardar borrador",
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

        container.rowconfigure(
            8,
            weight=1,
        )

        self.bind(
            "<Escape>",
            lambda _event: self._cancel(),
        )

    def _load_providers(self) -> None:
        descriptions: list[str] = []

        for proveedor in self.proveedores:
            description = (
                f"{proveedor.razon_social} "
                f"| CUIT {proveedor.cuit} "
                f"| {proveedor.aduana.codigo}"
            )

            descriptions.append(description)

            self.proveedor_por_descripcion[
                description
            ] = proveedor

        self.proveedor_combobox.configure(
            values=descriptions,
        )

        if descriptions and not self.is_editing:
            self.proveedor_var.set(
                descriptions[0]
            )

            self._update_customs_office()

    def _load_initial_values(self) -> None:
        if self.esquema is None:
            self.fecha_inicio_var.set(
                date.today().strftime(
                    "%d/%m/%Y"
                )
            )
            return

        proveedor = self.esquema.proveedor

        description = (
            f"{proveedor.razon_social} "
            f"| CUIT {proveedor.cuit} "
            f"| {proveedor.aduana.codigo}"
        )

        self.proveedor_var.set(description)

        self.aduana_var.set(
            f"{proveedor.aduana.codigo} - "
            f"{proveedor.aduana.nombre}"
        )

        self.fecha_inicio_var.set(
            self.esquema.fecha_inicio.strftime(
                "%d/%m/%Y"
            )
        )

        self.moneda_var.set(
            self.esquema.moneda_codigo
        )

        if self.esquema.observaciones:
            self.observaciones_text.insert(
                "1.0",
                self.esquema.observaciones,
            )

    def _provider_selected(
        self,
        _event: tk.Event | None = None,
    ) -> None:
        self._update_customs_office()

    def _update_customs_office(self) -> None:
        proveedor = self._selected_provider()

        if proveedor is None:
            self.aduana_var.set("")
            return

        self.aduana_var.set(
            f"{proveedor.aduana.codigo} - "
            f"{proveedor.aduana.nombre}"
        )

    def _selected_provider(
        self,
    ) -> Proveedor | None:
        description = self.proveedor_var.get()

        return self.proveedor_por_descripcion.get(
            description
        )

    def _save(self) -> None:
        proveedor = self._selected_provider()

        if proveedor is None:
            messagebox.showwarning(
                title="Proveedor obligatorio",
                message=(
                    "Selecciona un proveedor para "
                    "el esquema de cotización."
                ),
                parent=self,
            )
            return

        observaciones = self.observaciones_text.get(
            "1.0",
            tk.END,
        )

        try:
            if self.esquema is None:
                esquema_guardado = self.service.crear(
                    proveedor_id=proveedor.proveedor_id,
                    fecha_inicio=self.fecha_inicio_var.get(),
                    moneda_codigo=self.moneda_var.get(),
                    observaciones=observaciones,
                )   
                self.esquema_guardado_id = (
                    esquema_guardado.esquema_cotizacion_id
                )
            else:
                esquema_guardado = self.service.actualizar(
                esquema_cotizacion_id=(
                    self.esquema.esquema_cotizacion_id
                ),
                proveedor_id=proveedor.proveedor_id,
                fecha_inicio=self.fecha_inicio_var.get(),
                moneda_codigo=self.moneda_var.get(),
                observaciones=observaciones,
                )

                self.esquema_guardado_id = (
                    esquema_guardado.esquema_cotizacion_id
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
                    "al guardar el esquema.\n\n"
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