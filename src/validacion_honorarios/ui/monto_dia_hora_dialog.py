import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.services import (
    ApplicationError,
    TarifaDiaHoraService,
)


class MontoDiaHoraDialog(tk.Toplevel):
    """Asigna un mismo importe a una o varias posiciones horarias."""

    def __init__(
        self,
        parent: tk.Misc,
        service: TarifaDiaHoraService,
        esquema_cotizacion_id: int,
        dia_hora_ids: list[int],
        descripcion_seleccion: str,
        moneda_codigo: str,
        monto_inicial: str = "",
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = esquema_cotizacion_id
        self.dia_hora_ids = dia_hora_ids
        self.resultado_guardado = False
        self.monto_var = tk.StringVar(value=monto_inicial)

        self._configure_window()
        self._build_interface(
            descripcion_seleccion=descripcion_seleccion,
            moneda_codigo=moneda_codigo,
        )

        self.transient(parent)
        self.grab_set()
        self.wait_visibility()
        self.monto_entry.focus_set()
        self.monto_entry.selection_range(0, tk.END)

    def _configure_window(self) -> None:
        self.title("Asignar importe horario")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_interface(
        self,
        descripcion_seleccion: str,
        moneda_codigo: str,
    ) -> None:
        container = ttk.Frame(self, padding=20)
        container.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            container,
            text="Selección",
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(
            container,
            text=descripcion_seleccion,
            wraplength=460,
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=(4, 16),
        )

        ttk.Label(
            container,
            text=f"Importe adicional ({moneda_codigo})",
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 4))

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
            text="Formatos admitidos: 38000, 38000,50 o 38.000,50.",
            foreground="#555555",
        ).grid(row=4, column=0, sticky=tk.W, pady=(0, 20))

        buttons = ttk.Frame(container)
        buttons.grid(row=5, column=0, sticky=tk.E)

        ttk.Button(
            buttons,
            text="Cancelar",
            command=self._cancel,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            buttons,
            text="Asignar importe",
            command=self._save,
        ).pack(side=tk.LEFT)

        container.columnconfigure(0, weight=1)
        self.bind("<Return>", lambda _event: self._save())
        self.bind("<Escape>", lambda _event: self._cancel())

    def _save(self) -> None:
        try:
            self.service.establecer_montos(
                esquema_cotizacion_id=self.esquema_cotizacion_id,
                dia_hora_ids=self.dia_hora_ids,
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
                    "Se produjo un error al guardar los importes.\n\n"
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
