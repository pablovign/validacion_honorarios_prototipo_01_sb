"""Alta y edición de un tramo adicional de camiones con CustomTkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from validacion_honorarios.db.models import AdicionalCamiones
from validacion_honorarios.services import (
    AdicionalCamionesService,
    ApplicationError,
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


class TramoCamionesDialog(ctk.CTkToplevel):
    """Alta y edición de un tramo adicional de camiones."""

    def __init__(
        self,
        parent: tk.Misc,
        service: AdicionalCamionesService,
        esquema_cotizacion_id: int,
        tramo: AdicionalCamiones | None = None,
    ) -> None:
        super().__init__(parent)

        self.service = service
        self.esquema_cotizacion_id = esquema_cotizacion_id
        self.tramo = tramo
        self.resultado_guardado = False

        self.camion_desde_var = tk.StringVar()
        self.camion_hasta_var = tk.StringVar()

        self._configure_window()
        self._build_interface()
        self._load_initial_values()

        self.transient(parent)
        self.grab_set()

        self.after(100, lambda: self.camion_desde_entry.focus_set())

    @property
    def is_editing(self) -> bool:
        return self.tramo is not None

    def _configure_window(self) -> None:
        title = "Editar Tramo de Camiones" if self.is_editing else "Nuevo Tramo de Camiones"
        self.title(title)
        self.geometry("480x300")
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
            text="🚛 Rango / Tramo de Camiones",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        header_lbl.pack(anchor="w", padx=20, pady=(16, 12))

        # Campos en dos columnas
        row_fields = ctk.CTkFrame(container, fg_color="transparent")
        row_fields.pack(fill=tk.X, padx=20, pady=(0, 4))
        row_fields.columnconfigure(0, weight=1)
        row_fields.columnconfigure(1, weight=1)

        lbl_desde = ctk.CTkLabel(
            row_fields,
            text="Camión desde:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_desde.grid(row=0, column=0, sticky="w", padx=(0, 6))

        lbl_hasta = ctk.CTkLabel(
            row_fields,
            text="Camión hasta:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_hasta.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.camion_desde_entry = ctk.CTkEntry(
            row_fields,
            textvariable=self.camion_desde_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: 1",
        )
        self.camion_desde_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        self.camion_hasta_entry = ctk.CTkEntry(
            row_fields,
            textvariable=self.camion_hasta_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: 5 (o vacío)",
        )
        self.camion_hasta_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        hint_lbl = ctk.CTkLabel(
            container,
            text="* Los dos extremos son inclusivos. Deja «Camión hasta» vacío para indicar que el tramo no tiene límite superior (en adelante).",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
            wraplength=420,
            justify="left",
        )
        hint_lbl.pack(anchor="w", padx=20, pady=(8, 16))

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
        if self.tramo is None:
            return
        self.camion_desde_var.set(str(self.tramo.camion_desde))
        if self.tramo.camion_hasta is not None:
            self.camion_hasta_var.set(str(self.tramo.camion_hasta))

    def _save(self) -> None:
        try:
            if self.tramo is None:
                self.service.crear_tramo(
                    esquema_cotizacion_id=self.esquema_cotizacion_id,
                    camion_desde=self.camion_desde_var.get(),
                    camion_hasta=self.camion_hasta_var.get(),
                )
            else:
                self.service.actualizar_tramo(
                    adicional_camiones_id=self.tramo.adicional_camiones_id,
                    camion_desde=self.camion_desde_var.get(),
                    camion_hasta=self.camion_hasta_var.get(),
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
                    "Se produjo un error inesperado al guardar el tramo.\n\n"
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