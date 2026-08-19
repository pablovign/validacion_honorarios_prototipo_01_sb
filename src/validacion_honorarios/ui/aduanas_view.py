import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.services import (
    AduanaService,
    ApplicationError,
)
from validacion_honorarios.ui.aduana_dialog import (
    AduanaDialog,
)


class AduanasView(ttk.Frame):
    """Listado y administración de aduanas."""

    def __init__(
        self,
        parent: tk.Misc,
    ) -> None:
        super().__init__(
            parent,
            padding=20,
        )

        self.service = AduanaService()
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
            text="Aduanas",
            style="SectionTitle.TLabel",
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            header,
            text="Nueva aduana",
            command=self._new_customs_office,
        ).pack(
            side=tk.RIGHT,
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
            "codigo",
            "nombre",
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.table.heading(
            "codigo",
            text="Código",
        )

        self.table.heading(
            "nombre",
            text="Nombre",
        )

        self.table.column(
            "codigo",
            width=120,
            minwidth=90,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "nombre",
            width=500,
            minwidth=250,
            anchor=tk.W,
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )

        self.table.configure(
            yscrollcommand=scrollbar.set,
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scrollbar.grid(
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
            lambda _event: self._edit_customs_office(),
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
            command=self._edit_customs_office,
        ).pack(
            side=tk.RIGHT,
        )

        ttk.Button(
            action_frame,
            text="Eliminar",
            command=self._delete_customs_office,
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
        busqueda = self.busqueda_var.get()

        try:
            aduanas = self.service.listar(
                busqueda=busqueda,
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
                    "de aduanas.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._clear_table()

        for aduana in aduanas:
            self.table.insert(
                "",
                tk.END,
                iid=str(aduana.aduana_id),
                values=(
                    aduana.codigo,
                    aduana.nombre,
                ),
            )

        self.status_label.configure(
            text=(
                f"{len(aduanas)} "
                f"{'aduana' if len(aduanas) == 1 else 'aduanas'}"
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
                title="Seleccionar aduana",
                message=(
                    "Selecciona una aduana "
                    "del listado."
                ),
                parent=self,
            )
            return None

        return int(selected[0])

    def _new_customs_office(self) -> None:
        dialog = AduanaDialog(
            parent=self,
            service=self.service,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._load_data()

    def _edit_customs_office(self) -> None:
        aduana_id = self._selected_id()

        if aduana_id is None:
            return

        try:
            aduana = self.service.obtener(
                aduana_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo abrir",
                message=str(exc),
                parent=self,
            )
            return

        dialog = AduanaDialog(
            parent=self,
            service=self.service,
            aduana=aduana,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._load_data()

    def _delete_customs_office(self) -> None:
        aduana_id = self._selected_id()

        if aduana_id is None:
            return

        item = self.table.item(
            str(aduana_id)
        )

        values = item.get(
            "values",
            [],
        )

        description = (
            f"{values[0]} - {values[1]}"
            if len(values) >= 2
            else f"ID {aduana_id}"
        )

        confirmed = messagebox.askyesno(
            title="Eliminar aduana",
            message=(
                "¿Deseas eliminar la siguiente "
                "aduana?\n\n"
                f"{description}\n\n"
                "La operación no podrá realizarse "
                "si existen proveedores asociados."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(
                aduana_id
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
                    "la aduana.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._load_data()

        messagebox.showinfo(
            title="Aduana eliminada",
            message="La aduana se eliminó correctamente.",
            parent=self,
        )