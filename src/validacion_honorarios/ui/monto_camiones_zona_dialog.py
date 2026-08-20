import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from validacion_honorarios.services import (
    AdicionalCamionesService,
    ApplicationError,
)


class MontoCamionesZonaDialog(tk.Toplevel):
    """Edición de una tarifa unitaria por tramo y zona."""

    def __init__(
        self,
        parent: tk.Misc,
        service: AdicionalCamionesService,
        esquema_cotizacion_id: int,
        adicional_camiones_id: int,
        zona_id: int,
        tramo_descripcion: str,
        zona_nombre: str,
        moneda_codigo: str,
        monto_actual: Decimal | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = (
            esquema_cotizacion_id
        )
        self.adicional_camiones_id = (
            adicional_camiones_id
        )
        self.zona_id = zona_id

        self.resultado_guardado = False

        self.monto_var = tk.StringVar(
            value=(
                format(monto_actual, ".2f")
                if monto_actual is not None
                else ""
            )
        )

        self._configure_window()
        self._build_interface(
            tramo_descripcion=tramo_descripcion,
            zona_nombre=zona_nombre,
            moneda_codigo=moneda_codigo,
        )

        self.transient(parent)
        self.grab_set()

        self.wait_visibility()
        self.monto_entry.focus_set()
        self.monto_entry.selection_range(
            0,
            tk.END,
        )

    def _configure_window(self) -> None:
        self.title(
            "Tarifa adicional por camión"
        )
        self.resizable(False, False)

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

    def _build_interface(
        self,
        tramo_descripcion: str,
        zona_nombre: str,
        moneda_codigo: str,
    ) -> None:
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
            text=f"Tramo: {tramo_descripcion}",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
        )

        ttk.Label(
            container,
            text=f"Zona: {zona_nombre}",
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=(4, 18),
        )

        ttk.Label(
            container,
            text=(
                f"Importe unitario por camión "
                f"({moneda_codigo})"
            ),
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.monto_entry = ttk.Entry(
            container,
            textvariable=self.monto_var,
            width=30,
        )
        self.monto_entry.grid(
            row=3,
            column=0,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            container,
            text=(
                "El importe se aplica a cada camión "
                "comprendido en el tramo."
            ),
            foreground="#555555",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
            pady=(0, 20),
        )

        button_frame = ttk.Frame(
            container
        )
        button_frame.grid(
            row=5,
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
            text="Guardar tarifa",
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

    def _save(self) -> None:
        try:
            self.service.establecer_tarifa(
                esquema_cotizacion_id=(
                    self.esquema_cotizacion_id
                ),
                adicional_camiones_id=(
                    self.adicional_camiones_id
                ),
                zona_id=self.zona_id,
                monto=self.monto_var.get(),
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
                    "al guardar la tarifa.\n\n"
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