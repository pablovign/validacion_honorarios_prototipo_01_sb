import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from validacion_honorarios.services import (
    ApplicationError,
    ZonaTarifaService,
)


class MontoTarifaDialog(tk.Toplevel):
    """Edición del monto de una tarifa zona-canal."""

    def __init__(
        self,
        parent: tk.Misc,
        service: ZonaTarifaService,
        esquema_cotizacion_id: int,
        zona_id: int,
        canal_selectividad_id: int,
        zona_nombre: str,
        canal_nombre: str,
        moneda_codigo: str,
        monto_actual: Decimal | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = (
            esquema_cotizacion_id
        )
        self.zona_id = zona_id
        self.canal_selectividad_id = (
            canal_selectividad_id
        )

        self.resultado_guardado = False

        self.monto_var = tk.StringVar(
            value=(
                self._format_decimal(monto_actual)
                if monto_actual is not None
                else ""
            )
        )

        self._configure_window()
        self._build_interface(
            zona_nombre=zona_nombre,
            canal_nombre=canal_nombre,
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

    @staticmethod
    def _format_decimal(
        value: Decimal,
    ) -> str:
        return format(value, ".2f")

    def _configure_window(self) -> None:
        self.title("Tarifa por zona y canal")
        self.resizable(False, False)

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

    def _build_interface(
        self,
        zona_nombre: str,
        canal_nombre: str,
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
            text=f"Zona: {zona_nombre}",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
        )

        ttk.Label(
            container,
            text=f"Canal: {canal_nombre}",
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=(4, 18),
        )

        ttk.Label(
            container,
            text=f"Monto ({moneda_codigo})",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        self.monto_entry = ttk.Entry(
            container,
            textvariable=self.monto_var,
            width=28,
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
                "Formatos admitidos: 38000, "
                "38000,50 o 38.000,50."
            ),
            foreground="#555555",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
            pady=(0, 20),
        )

        button_frame = ttk.Frame(container)
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
                zona_id=self.zona_id,
                canal_selectividad_id=(
                    self.canal_selectividad_id
                ),
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
                    "Se produjo un error al guardar "
                    "la tarifa.\n\n"
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