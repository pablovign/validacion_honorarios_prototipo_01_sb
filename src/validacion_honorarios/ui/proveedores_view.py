import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import Aduana
from validacion_honorarios.services import (
    ApplicationError,
    ProveedorService,
)
from validacion_honorarios.ui.proveedor_dialog import (
    ProveedorDialog,
)


class ProveedoresView(ttk.Frame):
    """Listado y administración de proveedores."""

    ALL_CUSTOMS_OFFICES = "Todas las aduanas"

    def __init__(
        self,
        parent: tk.Misc,
    ) -> None:
        super().__init__(
            parent,
            padding=20,
        )

        self.service = ProveedorService()

        self.busqueda_var = tk.StringVar()
        self.aduana_filtro_var = tk.StringVar(
            value=self.ALL_CUSTOMS_OFFICES
        )

        self.aduana_por_descripcion: dict[
            str,
            Aduana,
        ] = {}

        self._build_interface()
        self._load_customs_office_filter()
        self._load_data()

    def _build_interface(self) -> None:
        header = ttk.Frame(self)
        header.pack(
            fill=tk.X,
            pady=(0, 16),
        )

        ttk.Label(
            header,
            text="Proveedores",
            style="SectionTitle.TLabel",
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            header,
            text="Nuevo proveedor",
            command=self._new_provider,
        ).pack(
            side=tk.RIGHT,
        )

        filters = ttk.Frame(self)
        filters.pack(
            fill=tk.X,
            pady=(0, 12),
        )

        ttk.Label(
            filters,
            text="Buscar:",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(0, 8),
        )

        search_entry = ttk.Entry(
            filters,
            textvariable=self.busqueda_var,
            width=32,
        )
        search_entry.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            padx=(0, 12),
        )

        search_entry.bind(
            "<Return>",
            lambda _event: self._load_data(),
        )

        ttk.Label(
            filters,
            text="Aduana:",
        ).grid(
            row=0,
            column=2,
            sticky=tk.W,
            padx=(0, 8),
        )

        self.aduana_filter = ttk.Combobox(
            filters,
            textvariable=self.aduana_filtro_var,
            state="readonly",
            width=32,
        )
        self.aduana_filter.grid(
            row=0,
            column=3,
            sticky=tk.EW,
            padx=(0, 12),
        )

        self.aduana_filter.bind(
            "<<ComboboxSelected>>",
            lambda _event: self._load_data(),
        )

        ttk.Button(
            filters,
            text="Buscar",
            command=self._load_data,
        ).grid(
            row=0,
            column=4,
            padx=(0, 8),
        )

        ttk.Button(
            filters,
            text="Limpiar",
            command=self._clear_filters,
        ).grid(
            row=0,
            column=5,
        )

        filters.columnconfigure(
            1,
            weight=1,
        )

        filters.columnconfigure(
            3,
            weight=1,
        )

        table_frame = ttk.Frame(self)
        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        columns = (
            "razon_social",
            "cuit",
            "aduana_codigo",
            "aduana_nombre",
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.table.heading(
            "razon_social",
            text="Razón social",
        )

        self.table.heading(
            "cuit",
            text="CUIT",
        )

        self.table.heading(
            "aduana_codigo",
            text="Código aduana",
        )

        self.table.heading(
            "aduana_nombre",
            text="Aduana",
        )

        self.table.column(
            "razon_social",
            width=320,
            minwidth=180,
            anchor=tk.W,
        )

        self.table.column(
            "cuit",
            width=130,
            minwidth=110,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "aduana_codigo",
            width=120,
            minwidth=100,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "aduana_nombre",
            width=240,
            minwidth=160,
            anchor=tk.W,
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.table.xview,
        )

        self.table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        table_frame.rowconfigure(
            0,
            weight=1,
        )

        table_frame.columnconfigure(
            0,
            weight=1,
        )

        self.table.bind(
            "<Double-1>",
            lambda _event: self._edit_provider(),
        )

        action_frame = ttk.Frame(self)
        action_frame.pack(
            fill=tk.X,
            pady=(12, 0),
        )

        ttk.Button(
            action_frame,
            text="Actualizar listado",
            command=self._refresh_all,
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            action_frame,
            text="Editar",
            command=self._edit_provider,
        ).pack(
            side=tk.RIGHT,
        )

        ttk.Button(
            action_frame,
            text="Eliminar",
            command=self._delete_provider,
        ).pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )

        self.status_label = ttk.Label(
            self,
            text="",
        )
        self.status_label.pack(
            fill=tk.X,
            pady=(10, 0),
        )

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

        values = [
            self.ALL_CUSTOMS_OFFICES
        ]

        for aduana in aduanas:
            description = (
                f"{aduana.codigo} - {aduana.nombre}"
            )

            values.append(description)
            self.aduana_por_descripcion[
                description
            ] = aduana

        self.aduana_filter.configure(
            values=values
        )

        if current_value in values:
            self.aduana_filtro_var.set(
                current_value
            )
        else:
            self.aduana_filtro_var.set(
                self.ALL_CUSTOMS_OFFICES
            )

    def _selected_customs_office_filter(
        self,
    ) -> int | None:
        description = (
            self.aduana_filtro_var.get()
        )

        if description == self.ALL_CUSTOMS_OFFICES:
            return None

        aduana = self.aduana_por_descripcion.get(
            description
        )

        if aduana is None:
            return None

        return aduana.aduana_id

    def _load_data(self) -> None:
        try:
            proveedores = self.service.listar(
                busqueda=self.busqueda_var.get(),
                aduana_id=(
                    self
                    ._selected_customs_office_filter()
                ),
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo consultar",
                message=str(exc),
                parent=self,
            )
            return

        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=(
                    "No se pudo recuperar el listado "
                    "de proveedores.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._clear_table()

        for proveedor in proveedores:
            aduana = proveedor.aduana

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
            )

        cantidad = len(proveedores)

        self.status_label.configure(
            text=(
                f"{cantidad} "
                f"{'proveedor' if cantidad == 1 else 'proveedores'}"
            )
        )

    def _clear_table(self) -> None:
        children = self.table.get_children()

        if children:
            self.table.delete(*children)

    def _clear_filters(self) -> None:
        self.busqueda_var.set("")
        self.aduana_filtro_var.set(
            self.ALL_CUSTOMS_OFFICES
        )
        self._load_data()

    def _refresh_all(self) -> None:
        self._load_customs_office_filter()
        self._load_data()

    def _selected_id(self) -> int | None:
        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                title="Seleccionar proveedor",
                message=(
                    "Selecciona un proveedor "
                    "del listado."
                ),
                parent=self,
            )
            return None

        return int(selected[0])

    def _new_provider(self) -> None:
        aduanas = self.service.listar_aduanas()

        if not aduanas:
            messagebox.showwarning(
                title="No hay aduanas",
                message=(
                    "Antes de crear un proveedor "
                    "debes registrar al menos "
                    "una aduana."
                ),
                parent=self,
            )
            return

        dialog = ProveedorDialog(
            parent=self,
            service=self.service,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _edit_provider(self) -> None:
        proveedor_id = self._selected_id()

        if proveedor_id is None:
            return

        try:
            proveedor = self.service.obtener(
                proveedor_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo abrir",
                message=str(exc),
                parent=self,
            )
            return

        dialog = ProveedorDialog(
            parent=self,
            service=self.service,
            proveedor=proveedor,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _delete_provider(self) -> None:
        proveedor_id = self._selected_id()

        if proveedor_id is None:
            return

        item = self.table.item(
            str(proveedor_id)
        )

        values = item.get(
            "values",
            [],
        )

        description = (
            f"{values[0]} - CUIT {values[1]}"
            if len(values) >= 2
            else f"ID {proveedor_id}"
        )

        confirmed = messagebox.askyesno(
            title="Eliminar proveedor",
            message=(
                "¿Deseas eliminar el siguiente "
                "proveedor?\n\n"
                f"{description}\n\n"
                "La operación no podrá realizarse "
                "si existen esquemas de cotización "
                "asociados."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(
                proveedor_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo eliminar",
                message=str(exc),
                parent=self,
            )
            return

        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=(
                    "Se produjo un error al eliminar "
                    "el proveedor.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._load_data()

        messagebox.showinfo(
            title="Proveedor eliminado",
            message=(
                "El proveedor se eliminó "
                "correctamente."
            ),
            parent=self,
        )