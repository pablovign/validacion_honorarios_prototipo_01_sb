import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.services import (
    ApplicationError,
    CanalSelectividadService,
)
from validacion_honorarios.ui.canal_selectividad_dialog import (
    CanalSelectividadDialog,
)


class CanalesSelectividadView(ttk.Frame):
    """Listado y administración de canales de selectividad."""

    def __init__(
        self,
        parent: tk.Misc,
    ) -> None:
        super().__init__(
            parent,
            padding=20,
        )

        self.service = CanalSelectividadService()
        self.busqueda_var = tk.StringVar()

        self._build_interface()
        self._load_data()

    def _build_interface(self) -> None:
        header = ttk.Frame(self)
        header.pack(
            fill=tk.X,
            pady=(0, 16),
        )

        ttk.Label(
            header,
            text="Canales de selectividad",
            style="SectionTitle.TLabel",
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            header,
            text="Nuevo canal",
            command=self._new_channel,
        ).pack(
            side=tk.RIGHT,
        )

        description = ttk.Label(
            self,
            text=(
                "Este catálogo contiene los canales que pueden "
                "utilizarse en las tarifas de los esquemas de "
                "cotización."
            ),
            wraplength=760,
        )
        description.pack(
            fill=tk.X,
            anchor=tk.W,
            pady=(0, 16),
        )

        search_frame = ttk.Frame(self)
        search_frame.pack(
            fill=tk.X,
            pady=(0, 12),
        )

        ttk.Label(
            search_frame,
            text="Buscar:",
        ).pack(
            side=tk.LEFT,
            padx=(0, 8),
        )

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.busqueda_var,
            width=40,
        )
        search_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
        )

        search_entry.bind(
            "<Return>",
            lambda _event: self._load_data(),
        )

        ttk.Button(
            search_frame,
            text="Buscar",
            command=self._load_data,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        ttk.Button(
            search_frame,
            text="Limpiar",
            command=self._clear_search,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        table_frame = ttk.Frame(self)
        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        columns = (
            "id",
            "nombre",
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.table.heading(
            "id",
            text="ID",
        )

        self.table.heading(
            "nombre",
            text="Nombre",
        )

        self.table.column(
            "id",
            width=100,
            minwidth=80,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "nombre",
            width=500,
            minwidth=250,
            anchor=tk.W,
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )

        self.table.configure(
            yscrollcommand=vertical_scrollbar.set,
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
            lambda _event: self._edit_channel(),
        )

        action_frame = ttk.Frame(self)
        action_frame.pack(
            fill=tk.X,
            pady=(12, 0),
        )

        ttk.Button(
            action_frame,
            text="Actualizar listado",
            command=self._load_data,
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            action_frame,
            text="Editar",
            command=self._edit_channel,
        ).pack(
            side=tk.RIGHT,
        )

        ttk.Button(
            action_frame,
            text="Eliminar",
            command=self._delete_channel,
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

    def _load_data(self) -> None:
        try:
            canales = self.service.listar(
                busqueda=self.busqueda_var.get(),
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
                    "de canales.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._clear_table()

        for canal in canales:
            self.table.insert(
                "",
                tk.END,
                iid=str(
                    canal.canal_selectividad_id
                ),
                values=(
                    canal.canal_selectividad_id,
                    canal.nombre,
                ),
            )

        cantidad = len(canales)

        self.status_label.configure(
            text=(
                f"{cantidad} "
                f"{'canal' if cantidad == 1 else 'canales'}"
            )
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
                message=(
                    "Selecciona un canal "
                    "del listado."
                ),
                parent=self,
            )
            return None

        return int(selected[0])

    def _new_channel(self) -> None:
        dialog = CanalSelectividadDialog(
            parent=self,
            service=self.service,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._load_data()

    def _edit_channel(self) -> None:
        canal_id = self._selected_id()

        if canal_id is None:
            return

        try:
            canal = self.service.obtener(
                canal_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo abrir",
                message=str(exc),
                parent=self,
            )
            return

        dialog = CanalSelectividadDialog(
            parent=self,
            service=self.service,
            canal=canal,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._load_data()

    def _delete_channel(self) -> None:
        canal_id = self._selected_id()

        if canal_id is None:
            return

        item = self.table.item(
            str(canal_id)
        )

        values = item.get(
            "values",
            [],
        )

        description = (
            str(values[1])
            if len(values) >= 2
            else f"ID {canal_id}"
        )

        confirmed = messagebox.askyesno(
            title="Eliminar canal",
            message=(
                "¿Deseas eliminar el siguiente "
                "canal de selectividad?\n\n"
                f"{description}\n\n"
                "La operación no podrá realizarse "
                "si existen tarifas asociadas."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(
                canal_id
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
                    "el canal.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._load_data()

        messagebox.showinfo(
            title="Canal eliminado",
            message=(
                "El canal se eliminó correctamente."
            ),
            parent=self,
        )