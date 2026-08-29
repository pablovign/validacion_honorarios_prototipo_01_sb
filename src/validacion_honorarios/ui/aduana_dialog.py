"""Ventana modal moderna para crear o modificar una aduana."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from validacion_honorarios.db.models import Aduana
from validacion_honorarios.services import AduanaService, ApplicationError
from validacion_honorarios.ui.theme import (
    COLOR_BG_MAIN,
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


class AduanaDialog(ctk.CTkToplevel):
    """Ventana modal moderna para crear o modificar una aduana."""

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

        self.after(100, lambda: self.codigo_entry.focus_set())

    @property
    def is_editing(self) -> bool:
        return self.aduana is not None

    def _configure_window(self) -> None:
        title = "Editar Aduana" if self.is_editing else "Nueva Aduana"
        self.title(title)
        self.geometry("480x320")
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

        # Header del Diálogo
        header_lbl = ctk.CTkLabel(
            container,
            text="🛃 Datos de la Aduana",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        header_lbl.pack(anchor="w", padx=20, pady=(16, 14))

        # Campo Código
        lbl_codigo = ctk.CTkLabel(
            container,
            text="Código:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_codigo.pack(anchor="w", padx=20, pady=(0, 2))

        self.codigo_entry = ctk.CTkEntry(
            container,
            textvariable=self.codigo_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: ADU01",
        )
        self.codigo_entry.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Campo Nombre
        lbl_nombre = ctk.CTkLabel(
            container,
            text="Nombre descriptivo:",
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
            placeholder_text="Ej: Aduana de Buenos Aires",
        )
        self.nombre_entry.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Botones de Acción
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
        if self.aduana is None:
            return

        self.codigo_var.set(self.aduana.codigo)
        self.nombre_var.set(self.aduana.nombre)

    def _save(self) -> None:
        codigo = self.codigo_var.get()
        nombre = self.nombre_var.get()

        try:
            if self.aduana is None:
                self.service.crear(codigo=codigo, nombre=nombre)
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
                    "Se produjo un error inesperado al guardar la aduana.\n\n"
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