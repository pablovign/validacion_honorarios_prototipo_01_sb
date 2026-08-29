"""Listado y administración moderna de canales de selectividad con CustomTkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from validacion_honorarios.services import ApplicationError, CanalSelectividadService
from validacion_honorarios.ui.canal_selectividad_dialog import CanalSelectividadDialog
from validacion_honorarios.ui.theme import (
    COLOR_BG_CARD,
    COLOR_BG_MAIN,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY,
    COLOR_SECONDARY_HOVER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    FONT_FAMILY,
    apply_treeview_row_tags,
    style_treeview,
)


class CanalesSelectividadView(ctk.CTkFrame):
    """Listado y administración de canales de selectividad."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.service = CanalSelectividadService()
        self.busqueda_var = tk.StringVar()

        self._build_interface()
        self._load_data()

    def _build_interface(self) -> None:
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=28, pady=(24, 16))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_frame,
            text="🎯 Canales de Selectividad",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_frame,
            text="Catálogo de canales para asignación de selectividad en esquemas.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_lbl.pack(anchor="w")

        btn_nuevo = ctk.CTkButton(
            header,
            text="+ Nuevo canal",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._new_channel,
        )
        btn_nuevo.pack(side="right")

        # Barra de Búsqueda
        search_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        search_card.pack(fill=tk.X, padx=28, pady=(0, 16), ipady=4)

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill=tk.X, padx=16, pady=8)

        lbl_buscar = ctk.CTkLabel(
            search_inner,
            text="Buscar:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_buscar.pack(side="left", padx=(0, 8))

        search_entry = ctk.CTkEntry(
            search_inner,
            textvariable=self.busqueda_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            placeholder_text="Escribe el nombre del canal...",
            height=34,
            corner_radius=6,
        )
        search_entry.pack(side="left", fill=tk.X, expand=True)
        search_entry.bind("<Return>", lambda _e: self._load_data())

        btn_buscar = ctk.CTkButton(
            search_inner,
            text="Buscar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=6,
            height=34,
            width=80,
            command=self._load_data,
        )
        btn_buscar.pack(side="left", padx=(8, 0))

        btn_limpiar = ctk.CTkButton(
            search_inner,
            text="Limpiar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=6,
            height=34,
            width=80,
            command=self._clear_search,
        )
        btn_limpiar.pack(side="left", padx=(8, 0))

        # Contenedor de la Tabla
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        table_card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))

        table_inner = ctk.CTkFrame(table_card, fg_color="transparent")
        table_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        table_inner.rowconfigure(0, weight=1)

        table_inner.columnconfigure(0, weight=1)

        columns = ("id", "nombre")
        self.table = ttk.Treeview(
            table_inner,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
        )

        self.table.heading("id", text="ID")
        self.table.heading("nombre", text="NOMBRE DEL CANAL")

        self.table.column("id", width=100, minwidth=80, anchor=tk.CENTER, stretch=False)
        self.table.column("nombre", width=600, minwidth=250, anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            table_inner,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.table.bind("<Double-1>", lambda _e: self._edit_channel())

        # Barra de Acciones
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=28, pady=(0, 24))

        self.status_label = ctk.CTkLabel(
            action_bar,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.pack(side="left")

        btn_eliminar = ctk.CTkButton(
            action_bar,
            text="Eliminar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            corner_radius=6,
            height=34,
            command=self._delete_channel,
        )
        btn_eliminar.pack(side="right", padx=(8, 0))

        btn_editar = ctk.CTkButton(
            action_bar,
            text="Editar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=6,
            height=34,
            command=self._edit_channel,
        )
        btn_editar.pack(side="right", padx=(8, 0))

        btn_refresh = ctk.CTkButton(
            action_bar,
            text="🔄 Actualizar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=6,
            height=34,
            command=self._load_data,
        )
        btn_refresh.pack(side="right")

    def _load_data(self) -> None:
        style_treeview()
        try:
            canales = self.service.listar(busqueda=self.busqueda_var.get())
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo consultar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=f"No se pudo recuperar el listado de canales.\n\nDetalle técnico:\n{exc}",
                parent=self,
            )
            return

        self._clear_table()
        apply_treeview_row_tags(self.table)

        for idx, canal in enumerate(canales):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.table.insert(
                "",
                tk.END,
                iid=str(canal.canal_selectividad_id),
                values=(canal.canal_selectividad_id, canal.nombre),
                tags=(tag,),
            )

        count = len(canales)
        self.status_label.configure(
            text=f"Total: {count} {'canal' if count == 1 else 'canales'} encontrados"
        )


    def _clear_table(self) -> None:
        children = self.table.get_children()
        if children:
            self.table.delete(*children)

    def _clear_search(self) -> None:
        self.busqueda_var.set("")
        self._load_data()

    def _selected_id(self) -> int | None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo(
                title="Seleccionar canal",
                message="Selecciona un canal del listado.",
                parent=self,
            )
            return None
        return int(selected[0])

    def _new_channel(self) -> None:
        dialog = CanalSelectividadDialog(parent=self, service=self.service)
        self.wait_window(dialog)
        if dialog.resultado_guardado:
            self._load_data()

    def _edit_channel(self) -> None:
        canal_id = self._selected_id()
        if canal_id is None:
            return

        try:
            canal = self.service.obtener(canal_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo abrir", message=str(exc), parent=self)
            return

        dialog = CanalSelectividadDialog(
            parent=self, service=self.service, canal=canal
        )
        self.wait_window(dialog)
        if dialog.resultado_guardado:
            self._load_data()

    def _delete_channel(self) -> None:
        canal_id = self._selected_id()
        if canal_id is None:
            return

        item = self.table.item(str(canal_id))
        values = item.get("values", [])
        description = str(values[1]) if len(values) >= 2 else f"ID {canal_id}"

        confirmed = messagebox.askyesno(
            title="Eliminar canal",
            message=(
                "¿Deseas eliminar el siguiente canal de selectividad?\n\n"
                f"{description}\n\n"
                "La operación no podrá realizarse si existen tarifas asociadas."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(canal_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=f"Se produjo un error al eliminar el canal.\n\nDetalle técnico:\n{exc}",
                parent=self,
            )
            return

        self._load_data()
        messagebox.showinfo(
            title="Canal eliminado",
            message="El canal se eliminó correctamente.",
            parent=self,
        )