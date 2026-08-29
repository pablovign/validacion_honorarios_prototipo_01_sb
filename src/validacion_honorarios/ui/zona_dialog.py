"""Ventana modal moderna para crear o modificar una zona."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from validacion_honorarios.db.models import Zona
from validacion_honorarios.services import ApplicationError, ZonaTarifaService
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


class ZonaDialog(ctk.CTkToplevel):
    """Ventana modal moderna para crear o modificar una zona."""

    def __init__(
        self,
        parent: tk.Misc,
        service: ZonaTarifaService,
        esquema_cotizacion_id: int,
        zona: Zona | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = esquema_cotizacion_id
        self.zona = zona

        self.resultado_guardado = False
        self.nombre_var = tk.StringVar()

        self._configure_window()
        self._build_interface()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.after(100, lambda: self.nombre_entry.focus_set())

    @property
    def is_editing(self) -> bool:
        return self.zona is not None

    def _configure_window(self) -> None:
        title = "Editar Zona" if self.is_editing else "Nueva Zona"
        self.title(title)
        self.geometry("480x290")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_interface(self) -> None:
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
            text="📍 Zona de Cotización",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        header_lbl.pack(anchor="w", padx=20, pady=(16, 14))

        # Campo Nombre
        lbl_nombre = ctk.CTkLabel(
            container,
            text="Nombre de la zona:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_nombre.pack(anchor="w", padx=20, pady=(0, 2))

        self.nombre_entry = ctk.CTkEntry(
            container,
            textvariable=self.nombre_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: ZONA NORTE, ZONA SUR, GENERAL...",
        )
        self.nombre_entry.pack(fill=tk.X, padx=20, pady=(0, 6))

        hint_lbl = ctk.CTkLabel(
            container,
            text="* Si el proveedor no diferencia zonas, puedes utilizar GENERAL.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        hint_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        # Botones
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 16), side="bottom")

        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="Guardar",
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

    def _load_initial_values(self) -> None:
        if self.zona is None:
            return
        self.nombre_var.set(self.zona.nombre)

    def _save(self) -> None:
        try:
            if self.zona is None:
                self.service.crear_zona(
                    esquema_cotizacion_id=self.esquema_cotizacion_id,
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
                    "Se produjo un error al guardar la zona.\n\n"
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