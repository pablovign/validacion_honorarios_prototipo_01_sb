"""Alta y edición moderna de la cabecera de un esquema con CustomTkinter."""

from __future__ import annotations

from datetime import date
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from validacion_honorarios.db.models import EsquemaCotizacion, Proveedor
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
)
from validacion_honorarios.ui.theme import (
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY,
    COLOR_SECONDARY_HOVER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    FONT_FAMILY,
)


class EsquemaCotizacionDialog(ctk.CTkToplevel):
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

        self.proveedor_por_descripcion: dict[str, Proveedor] = {}
        self.resultado_guardado = False
        self.esquema_guardado_id: int | None = None

        self.proveedor_var = tk.StringVar()
        self.aduana_var = tk.StringVar()
        self.fecha_inicio_var = tk.StringVar()
        self.moneda_var = tk.StringVar(value="ARS")

        self._configure_window()
        self._build_interface()
        self._load_providers()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.after(100, lambda: self.fecha_inicio_entry.focus_set())

    @property
    def is_editing(self) -> bool:
        return self.esquema is not None

    def _configure_window(self) -> None:
        title = (
            "Editar Esquema de Cotización"
            if self.is_editing
            else "Nuevo Esquema de Cotización"
        )
        self.title(title)
        self.geometry("640x580")
        self.minsize(580, 520)
        self.resizable(True, True)

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_interface(self) -> None:
        container = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Header
        header_lbl = ctk.CTkLabel(
            container,
            text="📋 Cabecera del Esquema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        header_lbl.pack(anchor="w", padx=16, pady=(12, 14))

        # Proveedor
        lbl_prov = ctk.CTkLabel(
            container,
            text="Proveedor:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_prov.pack(anchor="w", padx=16, pady=(0, 2))

        self.proveedor_option = ctk.CTkOptionMenu(
            container,
            variable=self.proveedor_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=36,
            corner_radius=8,
            command=self._provider_selected,
        )
        self.proveedor_option.pack(fill=tk.X, padx=16, pady=(0, 12))

        # Aduana Asociada
        lbl_aduana = ctk.CTkLabel(
            container,
            text="Aduana asociada:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_aduana.pack(anchor="w", padx=16, pady=(0, 2))

        self.aduana_entry = ctk.CTkEntry(
            container,
            textvariable=self.aduana_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            state="disabled",
        )
        self.aduana_entry.pack(fill=tk.X, padx=16, pady=(0, 12))

        # Fila Fecha y Moneda
        row_fm = ctk.CTkFrame(container, fg_color="transparent")
        row_fm.pack(fill=tk.X, padx=16, pady=(0, 4))
        row_fm.columnconfigure(0, weight=1)
        row_fm.columnconfigure(1, weight=1)

        lbl_f = ctk.CTkLabel(
            row_fm,
            text="Fecha de inicio (DD/MM/AAAA):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_f.grid(row=0, column=0, sticky="w", padx=(0, 6))

        lbl_m = ctk.CTkLabel(
            row_fm,
            text="Moneda:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_m.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.fecha_inicio_entry = ctk.CTkEntry(
            row_fm,
            textvariable=self.fecha_inicio_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="DD/MM/AAAA",
        )
        self.fecha_inicio_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        self.moneda_option = ctk.CTkOptionMenu(
            row_fm,
            variable=self.moneda_var,
            values=["ARS", "USD"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=36,
            corner_radius=8,
        )
        self.moneda_option.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # Observaciones
        lbl_obs = ctk.CTkLabel(
            container,
            text="Observaciones / Notas:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_obs.pack(anchor="w", padx=16, pady=(12, 2))

        self.observaciones_text = ctk.CTkTextbox(
            container,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=90,
            corner_radius=8,
        )
        self.observaciones_text.pack(fill=tk.X, padx=16, pady=(0, 16))

        # Botones
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="Guardar Esquema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._save,
        )
        btn_guardar.pack(side="right", padx=(8, 0))

        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._cancel,
        )
        btn_cancelar.pack(side="right")

    def _load_providers(self) -> None:
        descriptions: list[str] = []
        for proveedor in self.proveedores:
            description = (
                f"{proveedor.razon_social} | CUIT {proveedor.cuit}"
            )
            descriptions.append(description)
            self.proveedor_por_descripcion[description] = proveedor

        if descriptions:
            self.proveedor_option.configure(values=descriptions)
            if not self.is_editing:
                self.proveedor_var.set(descriptions[0])
                self._provider_selected(descriptions[0])

    def _load_initial_values(self) -> None:
        if self.esquema is None:
            self.fecha_inicio_var.set(date.today().strftime("%d/%m/%Y"))
            return

        proveedor = self.esquema.proveedor
        description = f"{proveedor.razon_social} | CUIT {proveedor.cuit}"
        self.proveedor_var.set(description)
        self._provider_selected(description)

        self.fecha_inicio_var.set(self.esquema.fecha_inicio.strftime("%d/%m/%Y"))
        self.moneda_var.set(self.esquema.moneda_codigo)

        if self.esquema.observaciones:
            self.observaciones_text.insert("1.0", self.esquema.observaciones)

        if self.is_editing:
            self.proveedor_option.configure(state="disabled")

    def _provider_selected(self, description: str | None = None) -> None:
        if description is None:
            description = self.proveedor_var.get()

        proveedor = self.proveedor_por_descripcion.get(description)
        if proveedor is None:
            self.aduana_var.set("")
            return

        aduana = proveedor.aduana
        self.aduana_var.set(f"{aduana.codigo} - {aduana.nombre}")

    def _selected_provider_id(self) -> int | None:
        description = self.proveedor_var.get()
        proveedor = self.proveedor_por_descripcion.get(description)
        if proveedor is None:
            messagebox.showwarning(
                title="Proveedor obligatorio",
                message="Selecciona un proveedor para el esquema.",
                parent=self,
            )
            return None
        return proveedor.proveedor_id

    def _save(self) -> None:
        proveedor_id = self._selected_provider_id()
        if proveedor_id is None:
            return

        fecha_inicio_str = self.fecha_inicio_var.get().strip()
        moneda_codigo = self.moneda_var.get().strip()
        observaciones = self.observaciones_text.get("1.0", tk.END).strip()

        try:
            if self.esquema is None:
                esquema = self.service.crear_esquema(
                    proveedor_id=proveedor_id,
                    fecha_inicio_str=fecha_inicio_str,
                    moneda_codigo=moneda_codigo,
                    observaciones=observaciones or None,
                )
                self.esquema_guardado_id = esquema.esquema_cotizacion_id
            else:
                self.service.actualizar_cabecera(
                    esquema_cotizacion_id=self.esquema.esquema_cotizacion_id,
                    fecha_inicio_str=fecha_inicio_str,
                    moneda_codigo=moneda_codigo,
                    observaciones=observaciones or None,
                )
                self.esquema_guardado_id = self.esquema.esquema_cotizacion_id
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
                message=f"Se produjo un error al guardar el esquema.\n\n{exc}",
                parent=self,
            )
            return

        self.resultado_guardado = True
        self.destroy()

    def _cancel(self) -> None:
        self.resultado_guardado = False
        self.destroy()