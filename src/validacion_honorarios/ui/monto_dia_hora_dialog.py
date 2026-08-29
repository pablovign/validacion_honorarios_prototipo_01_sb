"""Asignación de importe horario con CustomTkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from validacion_honorarios.services import ApplicationError, TarifaDiaHoraService
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


class MontoDiaHoraDialog(ctk.CTkToplevel):
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

        self.after(100, lambda: self._set_focus())

    def _set_focus(self) -> None:
        self.monto_entry.focus_set()
        self.monto_entry.select_range(0, tk.END)

    def _configure_window(self) -> None:
        self.title("Asignar Importe Horario")
        self.geometry("500x340")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_interface(
        self,
        descripcion_seleccion: str,
        moneda_codigo: str,
    ) -> None:
        container = ctk.CTkFrame(
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
            text="⏰ Importe Adicional Día y Hora",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        header_lbl.pack(anchor="w", padx=20, pady=(16, 10))

        # Información selección
        info_frame = ctk.CTkFrame(container, fg_color=COLOR_BORDER, corner_radius=8)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 14), ipady=6, ipadx=8)

        lbl_desc = ctk.CTkLabel(
            info_frame,
            text=f"Selección: {descripcion_seleccion}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_PRIMARY,
            wraplength=420,
            justify="left",
        )
        lbl_desc.pack(anchor="w", padx=10, pady=2)

        # Campo Monto
        lbl_monto = ctk.CTkLabel(
            container,
            text=f"Importe adicional ({moneda_codigo}):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_monto.pack(anchor="w", padx=20, pady=(0, 2))

        self.monto_entry = ctk.CTkEntry(
            container,
            textvariable=self.monto_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: 15000.00",
        )
        self.monto_entry.pack(fill=tk.X, padx=20, pady=(0, 4))

        lbl_hint = ctk.CTkLabel(
            container,
            text="* Formatos admitidos: 38000, 38000,50 o 38.000,50",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_hint.pack(anchor="w", padx=20, pady=(0, 16))

        # Botones
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 16), side="bottom")

        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="Asignar Importe",
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

        self.bind("<Return>", lambda _e: self._save())
        self.bind("<Escape>", lambda _e: self._cancel())

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
