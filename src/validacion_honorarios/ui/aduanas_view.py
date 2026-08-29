"""Listado y administración moderna de aduanas con CustomTkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from validacion_honorarios.services import AduanaService, ApplicationError
from validacion_honorarios.ui.aduana_dialog import AduanaDialog
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
    style_treeview,
)


class AduanasView(ctk.CTkFrame):
    """Listado y administración de aduanas."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.service = AduanaService()
        self.busqueda_var = tk.StringVar()

        self._build_interface()
        self._load_data()

    def _build_interface(self) -> None:
        # Header / Barra Superior
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=28, pady=(24, 16))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_frame,
            text="🛃 Aduanas",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_frame,
            text="Gestiona los puntos aduaneros para la parametrización de tarifas.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_lbl.pack(anchor="w")

        btn_nueva = ctk.CTkButton(
            header,
            text="+ Nueva aduana",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._new_customs_office,
        )
        btn_nueva.pack(side="right")

        # Barra de Filtros y Búsqueda
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
            placeholder_text="Escribe código o nombre de aduana...",
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

        # Contenedor de la Tabla con Card Styling
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

        columns = ("codigo", "nombre")
        self.table = ttk.Treeview(
            table_inner,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
        )

        self.table.heading("codigo", text="CÓDIGO")
        self.table.heading("nombre", text="NOMBRE DE ADUANA")

        self.table.column("codigo", width=140, minwidth=100, anchor=tk.CENTER, stretch=False)
        self.table.column("nombre", width=600, minwidth=250, anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            table_inner,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.table.bind("<Double-1>", lambda _e: self._edit_customs_office())

        # Barra Inferior de Acciones
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
            command=self._delete_customs_office,
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
            command=self._edit_customs_office,
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
        busqueda = self.busqueda_var.get()

        try:
            aduanas = self.service.listar(busqueda=busqueda)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo consultar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=f"No se pudo recuperar el listado de aduanas.\n\nDetalle técnico:\n{exc}",
                parent=self,
            )
            return

        self._clear_table()

        for aduana in aduanas:
            self.table.insert(
                "",
                tk.END,
                iid=str(aduana.aduana_id),
                values=(aduana.codigo, aduana.nombre),
            )

        count = len(aduanas)
        self.status_label.configure(
            text=f"Total: {count} {'aduana' if count == 1 else 'aduanas'} encontradas"
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
                title="Seleccionar aduana",
                message="Selecciona una aduana del listado.",
                parent=self,
            )
            return None
        return int(selected[0])

    def _new_customs_office(self) -> None:
        dialog = AduanaDialog(parent=self, service=self.service)
        self.wait_window(dialog)
        if dialog.resultado_guardado:
            self._load_data()

    def _edit_customs_office(self) -> None:
        aduana_id = self._selected_id()
        if aduana_id is None:
            return

        try:
            aduana = self.service.obtener(aduana_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo abrir", message=str(exc), parent=self)
            return

        dialog = AduanaDialog(parent=self, service=self.service, aduana=aduana)
        self.wait_window(dialog)
        if dialog.resultado_guardado:
            self._load_data()

    def _delete_customs_office(self) -> None:
        aduana_id = self._selected_id()
        if aduana_id is None:
            return

        item = self.table.item(str(aduana_id))
        values = item.get("values", [])
        description = (
            f"{values[0]} - {values[1]}"
            if len(values) >= 2
            else f"ID {aduana_id}"
        )

        confirmed = messagebox.askyesno(
            title="Eliminar aduana",
            message=(
                "¿Deseas eliminar la siguiente aduana?\n\n"
                f"{description}\n\n"
                "La operación no podrá realizarse si existen proveedores asociados."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(aduana_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=f"Se produjo un error al eliminar la aduana.\n\nDetalle técnico:\n{exc}",
                parent=self,
            )
            return

        self._load_data()
        messagebox.showinfo(
            title="Aduana eliminada",
            message="La aduana se eliminó correctamente.",
            parent=self,
        )