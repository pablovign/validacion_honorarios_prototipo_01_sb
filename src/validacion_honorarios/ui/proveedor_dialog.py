"""Ventana modal moderna para crear o modificar un proveedor."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from validacion_honorarios.db.models import Aduana, Proveedor
from validacion_honorarios.services import ApplicationError, ProveedorService
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


class ProveedorDialog(ctk.CTkToplevel):
    """Ventana modal moderna para crear o modificar un proveedor."""

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

        self.after(100, lambda: self.razon_social_entry.focus_set())

    @property
    def is_editing(self) -> bool:
        return self.proveedor is not None

    def _configure_window(self) -> None:
        title = "Editar Proveedor" if self.is_editing else "Nuevo Proveedor"
        self.title(title)
        self.geometry("520x420")
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
            text="🏢 Datos del Proveedor",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        header_lbl.pack(anchor="w", padx=20, pady=(16, 14))

        # Campo Razón Social
        lbl_razon = ctk.CTkLabel(
            container,
            text="Razón Social:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_razon.pack(anchor="w", padx=20, pady=(0, 2))

        self.razon_social_entry = ctk.CTkEntry(
            container,
            textvariable=self.razon_social_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: Logística Internacional S.A.",
        )
        self.razon_social_entry.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Campo CUIT
        lbl_cuit = ctk.CTkLabel(
            container,
            text="CUIT / Identificación Fiscal:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_cuit.pack(anchor="w", padx=20, pady=(0, 2))

        self.cuit_entry = ctk.CTkEntry(
            container,
            textvariable=self.cuit_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            placeholder_text="Ej: 30-12345678-9",
        )
        self.cuit_entry.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Campo Aduana
        lbl_aduana = ctk.CTkLabel(
            container,
            text="Aduana asignada:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_aduana.pack(anchor="w", padx=20, pady=(0, 2))

        self.aduana_option = ctk.CTkOptionMenu(
            container,
            variable=self.aduana_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=36,
            corner_radius=8,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
        )
        self.aduana_option.pack(fill=tk.X, padx=20, pady=(0, 20))

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

    def _load_customs_offices(self) -> None:
        descriptions: list[str] = []

        for aduana in self.aduanas:
            description = f"{aduana.codigo} - {aduana.nombre}"
            descriptions.append(description)
            self.aduana_por_descripcion[description] = aduana

        if descriptions:
            self.aduana_option.configure(values=descriptions)
            if not self.is_editing:
                self.aduana_var.set(descriptions[0])
        else:
            self.aduana_option.configure(values=["(Sin aduanas registradas)"])
            self.aduana_var.set("(Sin aduanas registradas)")

    def _load_initial_values(self) -> None:
        if self.proveedor is None:
            return

        self.razon_social_var.set(self.proveedor.razon_social)
        self.cuit_var.set(self.proveedor.cuit)

        description = f"{self.proveedor.aduana.codigo} - {self.proveedor.aduana.nombre}"
        self.aduana_var.set(description)

    def _selected_customs_office_id(self) -> int | None:
        description = self.aduana_var.get()
        aduana = self.aduana_por_descripcion.get(description)

        if aduana is None:
            messagebox.showwarning(
                title="Aduana obligatoria",
                message="Selecciona una aduana válida para el proveedor.",
                parent=self,
            )
            return None

        return aduana.aduana_id

    def _save(self) -> None:
        aduana_id = self._selected_customs_office_id()
        if aduana_id is None:
            return

        try:
            if self.proveedor is None:
                self.service.crear(
                    aduana_id=aduana_id,
                    razon_social=self.razon_social_var.get(),
                    cuit=self.cuit_var.get(),
                )
            else:
                self.service.actualizar(
                    proveedor_id=self.proveedor.proveedor_id,
                    aduana_id=aduana_id,
                    razon_social=self.razon_social_var.get(),
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
                    "Se produjo un error inesperado al guardar el proveedor.\n\n"
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