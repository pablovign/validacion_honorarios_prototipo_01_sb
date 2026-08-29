"""Listado y administración moderna de proveedores con CustomTkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from validacion_honorarios.db.models import Aduana
from validacion_honorarios.services import ApplicationError, ProveedorService
from validacion_honorarios.ui.proveedor_dialog import ProveedorDialog
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


class ProveedoresView(ctk.CTkFrame):
    """Listado y administración de proveedores."""

    ALL_CUSTOMS_OFFICES = "Todas las aduanas"

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.service = ProveedorService()

        self.busqueda_var = tk.StringVar()
        self.aduana_filtro_var = tk.StringVar(value=self.ALL_CUSTOMS_OFFICES)
        self.aduana_por_descripcion: dict[str, Aduana] = {}

        self._build_interface()
        self._load_customs_office_filter()
        self._load_data()

    def _build_interface(self) -> None:
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=28, pady=(24, 16))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_frame,
            text="🏢 Proveedores",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_frame,
            text="Administración de proveedores aduaneros y datos fiscales.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_lbl.pack(anchor="w")

        btn_nuevo = ctk.CTkButton(
            header,
            text="+ Nuevo proveedor",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._new_provider,
        )
        btn_nuevo.pack(side="right")

        # Barra de Filtros y Búsqueda
        filter_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        filter_card.pack(fill=tk.X, padx=28, pady=(0, 16), ipady=4)

        filter_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_inner.pack(fill=tk.X, padx=16, pady=8)

        lbl_buscar = ctk.CTkLabel(
            filter_inner,
            text="Buscar:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_buscar.pack(side="left", padx=(0, 8))

        search_entry = ctk.CTkEntry(
            filter_inner,
            textvariable=self.busqueda_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            placeholder_text="Buscar por Razón Social o CUIT...",
            height=34,
            corner_radius=6,
        )
        search_entry.pack(side="left", fill=tk.X, expand=True, padx=(0, 12))
        search_entry.bind("<Return>", lambda _e: self._load_data())

        lbl_aduana = ctk.CTkLabel(
            filter_inner,
            text="Aduana:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_aduana.pack(side="left", padx=(0, 8))

        self.aduana_option = ctk.CTkOptionMenu(
            filter_inner,
            variable=self.aduana_filtro_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=34,
            corner_radius=6,
            command=lambda _val: self._load_data(),
        )
        self.aduana_option.pack(side="left", padx=(0, 12))

        btn_buscar = ctk.CTkButton(
            filter_inner,
            text="Buscar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=6,
            height=34,
            width=80,
            command=self._load_data,
        )
        btn_buscar.pack(side="left", padx=(0, 8))

        btn_limpiar = ctk.CTkButton(
            filter_inner,
            text="Limpiar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=6,
            height=34,
            width=80,
            command=self._clear_filters,
        )
        btn_limpiar.pack(side="left")

        # Contenedor de la Tabla
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        table_card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))

        table_inner = tk.Frame(table_card, bg="")
        table_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        table_inner.rowconfigure(0, weight=1)
        table_inner.columnconfigure(0, weight=1)

        columns = (
            "razon_social",
            "cuit",
            "aduana_codigo",
            "aduana_nombre",
        )

        self.table = ttk.Treeview(
            table_inner,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
        )

        self.table.heading("razon_social", text="RAZÓN SOCIAL")
        self.table.heading("cuit", text="CUIT / IDENTIFICACIÓN")
        self.table.heading("aduana_codigo", text="CÓD. ADUANA")
        self.table.heading("aduana_nombre", text="ADUANA")

        self.table.column("razon_social", width=340, minwidth=180, anchor=tk.W)
        self.table.column("cuit", width=140, minwidth=110, anchor=tk.CENTER, stretch=False)
        self.table.column("aduana_codigo", width=120, minwidth=100, anchor=tk.CENTER, stretch=False)
        self.table.column("aduana_nombre", width=260, minwidth=160, anchor=tk.W)

        vertical_scrollbar = ttk.Scrollbar(
            table_inner,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_inner,
            orient=tk.HORIZONTAL,
            command=self.table.xview,
        )

        self.table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.table.bind("<Double-1>", lambda _e: self._edit_provider())

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
            command=self._delete_provider,
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
            command=self._edit_provider,
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
            command=self._refresh_all,
        )
        btn_refresh.pack(side="right")

    def _load_customs_office_filter(self) -> None:
        try:
            aduanas = self.service.listar_aduanas()
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudieron cargar las aduanas",
                message=str(exc),
                parent=self,
            )
            return

        current_value = self.aduana_filtro_var.get()
        self.aduana_por_descripcion.clear()

        values = [self.ALL_CUSTOMS_OFFICES]
        for aduana in aduanas:
            description = f"{aduana.codigo} - {aduana.nombre}"
            values.append(description)
            self.aduana_por_descripcion[description] = aduana

        self.aduana_option.configure(values=values)
        if current_value in values:
            self.aduana_filtro_var.set(current_value)
        else:
            self.aduana_filtro_var.set(self.ALL_CUSTOMS_OFFICES)

    def _selected_customs_office_filter(self) -> int | None:
        description = self.aduana_filtro_var.get()
        if description == self.ALL_CUSTOMS_OFFICES:
            return None
        aduana = self.aduana_por_descripcion.get(description)
        return aduana.aduana_id if aduana else None

    def _load_data(self) -> None:
        style_treeview()
        try:
            proveedores = self.service.listar(
                busqueda=self.busqueda_var.get(),
                aduana_id=self._selected_customs_office_filter(),
            )
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo consultar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=f"No se pudo recuperar el listado de proveedores.\n\nDetalle técnico:\n{exc}",
                parent=self,
            )
            return

        self._clear_table()
        apply_treeview_row_tags(self.table)

        for idx, proveedor in enumerate(proveedores):
            aduana = proveedor.aduana
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.table.insert(
                "",
                tk.END,
                iid=str(proveedor.proveedor_id),
                values=(
                    proveedor.razon_social,
                    proveedor.cuit,
                    aduana.codigo,
                    aduana.nombre,
                ),
                tags=(tag,),
            )

        cantidad = len(proveedores)
        self.status_label.configure(
            text=f"Total: {cantidad} {'proveedor' if cantidad == 1 else 'proveedores'} encontrados"
        )


    def _clear_table(self) -> None:
        children = self.table.get_children()
        if children:
            self.table.delete(*children)

    def _clear_filters(self) -> None:
        self.busqueda_var.set("")
        self.aduana_filtro_var.set(self.ALL_CUSTOMS_OFFICES)
        self._load_data()

    def _refresh_all(self) -> None:
        self._load_customs_office_filter()
        self._load_data()

    def _selected_id(self) -> int | None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo(
                title="Seleccionar proveedor",
                message="Selecciona un proveedor del listado.",
                parent=self,
            )
            return None
        return int(selected[0])

    def _new_provider(self) -> None:
        aduanas = self.service.listar_aduanas()
        if not aduanas:
            messagebox.showwarning(
                title="No hay aduanas",
                message="Antes de crear un proveedor debes registrar al menos una aduana.",
                parent=self,
            )
            return

        dialog = ProveedorDialog(parent=self, service=self.service)
        self.wait_window(dialog)
        if dialog.resultado_guardado:
            self._refresh_all()

    def _edit_provider(self) -> None:
        proveedor_id = self._selected_id()
        if proveedor_id is None:
            return

        try:
            proveedor = self.service.obtener(proveedor_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo abrir", message=str(exc), parent=self)
            return

        dialog = ProveedorDialog(parent=self, service=self.service, proveedor=proveedor)
        self.wait_window(dialog)
        if dialog.resultado_guardado:
            self._refresh_all()

    def _delete_provider(self) -> None:
        proveedor_id = self._selected_id()
        if proveedor_id is None:
            return

        item = self.table.item(str(proveedor_id))
        values = item.get("values", [])
        description = (
            f"{values[0]} - CUIT {values[1]}"
            if len(values) >= 2
            else f"ID {proveedor_id}"
        )

        confirmed = messagebox.askyesno(
            title="Eliminar proveedor",
            message=(
                "¿Deseas eliminar el siguiente proveedor?\n\n"
                f"{description}\n\n"
                "La operación no podrá realizarse si existen esquemas de cotización asociados."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(proveedor_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=f"Se produjo un error al eliminar el proveedor.\n\nDetalle técnico:\n{exc}",
                parent=self,
            )
            return

        self._load_data()
        messagebox.showinfo(
            title="Proveedor eliminado",
            message="El proveedor se eliminó correctamente.",
            parent=self,
        )