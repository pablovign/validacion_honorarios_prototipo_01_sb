import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    Aduana,
    Proveedor,
)
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
)
from validacion_honorarios.ui.esquema_cotizacion_dialog import (
    EsquemaCotizacionDialog,
)
from validacion_honorarios.ui.completar_esquema_window import (
    CompletarEsquemaWindow,
)

class EsquemasCotizacionView(ttk.Frame):
    """Listado y gestión inicial de esquemas."""

    ALL_PROVIDERS = "Todos los proveedores"
    ALL_CUSTOMS_OFFICES = "Todas las aduanas"
    ALL_STATES = "Todos los estados"
    ALL_CURRENCIES = "Todas las monedas"

    def __init__(
        self,
        parent: tk.Misc,
    ) -> None:
        super().__init__(
            parent,
            padding=20,
        )

        self.service = EsquemaCotizacionService()

        self.busqueda_var = tk.StringVar()

        self.proveedor_filtro_var = tk.StringVar(
            value=self.ALL_PROVIDERS
        )

        self.aduana_filtro_var = tk.StringVar(
            value=self.ALL_CUSTOMS_OFFICES
        )

        self.estado_filtro_var = tk.StringVar(
            value=self.ALL_STATES
        )

        self.moneda_filtro_var = tk.StringVar(
            value=self.ALL_CURRENCIES
        )

        self.proveedor_por_descripcion: dict[
            str,
            Proveedor,
        ] = {}

        self.aduana_por_descripcion: dict[
            str,
            Aduana,
        ] = {}

        self._build_interface()
        self._load_filter_values()
        self._load_data()

    def _build_interface(self) -> None:
        header = ttk.Frame(self)
        header.pack(
            fill=tk.X,
            pady=(0, 14),
        )

        ttk.Label(
            header,
            text="Esquemas de cotización",
            style="SectionTitle.TLabel",
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            header,
            text="Nuevo esquema",
            command=self._new_quote,
        ).pack(
            side=tk.RIGHT,
        )

        ttk.Label(
            self,
            text=(
                "La cabecera identifica el proveedor, "
                "la vigencia propuesta y la moneda. "
                "Los componentes tarifarios se completarán "
                "posteriormente."
            ),
            wraplength=900,
        ).pack(
            fill=tk.X,
            anchor=tk.W,
            pady=(0, 14),
        )

        filter_container = ttk.LabelFrame(
            self,
            text="Filtros",
            padding=12,
        )
        filter_container.pack(
            fill=tk.X,
            pady=(0, 12),
        )

        ttk.Label(
            filter_container,
            text="Buscar",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 4),
        )

        ttk.Label(
            filter_container,
            text="Proveedor",
        ).grid(
            row=0,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=(0, 4),
        )

        ttk.Label(
            filter_container,
            text="Aduana",
        ).grid(
            row=0,
            column=2,
            sticky=tk.W,
            padx=(10, 0),
            pady=(0, 4),
        )

        self.search_entry = ttk.Entry(
            filter_container,
            textvariable=self.busqueda_var,
            width=24,
        )
        self.search_entry.grid(
            row=1,
            column=0,
            sticky=tk.EW,
        )

        self.search_entry.bind(
            "<Return>",
            lambda _event: self._load_data(),
        )

        self.proveedor_filter = ttk.Combobox(
            filter_container,
            textvariable=self.proveedor_filtro_var,
            state="readonly",
            width=28,
        )
        self.proveedor_filter.grid(
            row=1,
            column=1,
            sticky=tk.EW,
            padx=(10, 0),
        )

        self.aduana_filter = ttk.Combobox(
            filter_container,
            textvariable=self.aduana_filtro_var,
            state="readonly",
            width=27,
        )
        self.aduana_filter.grid(
            row=1,
            column=2,
            sticky=tk.EW,
            padx=(10, 0),
        )

        ttk.Label(
            filter_container,
            text="Estado",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(10, 4),
        )

        ttk.Label(
            filter_container,
            text="Moneda",
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=(10, 4),
        )

        self.estado_filter = ttk.Combobox(
            filter_container,
            textvariable=self.estado_filtro_var,
            state="readonly",
            values=(
                self.ALL_STATES,
                "BORRADOR",
                "APROBADO",
                "RECHAZADO",
            ),
        )
        self.estado_filter.grid(
            row=3,
            column=0,
            sticky=tk.EW,
        )

        self.moneda_filter = ttk.Combobox(
            filter_container,
            textvariable=self.moneda_filtro_var,
            state="readonly",
            values=(
                self.ALL_CURRENCIES,
                "ARS",
                "USD",
            ),
        )
        self.moneda_filter.grid(
            row=3,
            column=1,
            sticky=tk.EW,
            padx=(10, 0),
        )

        button_frame = ttk.Frame(
            filter_container
        )
        button_frame.grid(
            row=3,
            column=2,
            sticky=tk.E,
            padx=(10, 0),
        )

        ttk.Button(
            button_frame,
            text="Aplicar filtros",
            command=self._load_data,
        ).pack(
            side=tk.LEFT,
            padx=(0, 8),
        )

        ttk.Button(
            button_frame,
            text="Limpiar",
            command=self._clear_filters,
        ).pack(
            side=tk.LEFT,
        )

        for column in range(3):
            filter_container.columnconfigure(
                column,
                weight=1,
            )

        for combobox in (
            self.proveedor_filter,
            self.aduana_filter,
            self.estado_filter,
            self.moneda_filter,
        ):
            combobox.bind(
                "<<ComboboxSelected>>",
                lambda _event: self._load_data(),
            )

        table_frame = ttk.Frame(self)
        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        columns = (
            "id",
            "proveedor",
            "cuit",
            "aduana",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "moneda",
            "zonas",
            "camiones",
            "horario",
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID",
            "proveedor": "Proveedor",
            "cuit": "CUIT",
            "aduana": "Aduana",
            "fecha_inicio": "Inicio",
            "fecha_fin": "Fin",
            "estado": "Estado",
            "moneda": "Moneda",
            "zonas": "Zonas",
            "camiones": "Tramos",
            "horario": "Horario",
        }

        for column, heading in headings.items():
            self.table.heading(
                column,
                text=heading,
            )

        self.table.column(
            "id",
            width=65,
            minwidth=55,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "proveedor",
            width=240,
            minwidth=180,
            anchor=tk.W,
        )

        self.table.column(
            "cuit",
            width=118,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "aduana",
            width=160,
            minwidth=120,
            anchor=tk.W,
        )

        self.table.column(
            "fecha_inicio",
            width=95,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "fecha_fin",
            width=95,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "estado",
            width=100,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "moneda",
            width=75,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "zonas",
            width=65,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "camiones",
            width=70,
            anchor=tk.CENTER,
            stretch=False,
        )

        self.table.column(
            "horario",
            width=75,
            anchor=tk.CENTER,
            stretch=False,
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
            lambda _event: self._edit_quote(),
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
            text="Completar esquema",
            command=self._complete_quote,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        ttk.Button(
            action_frame,
            text="Editar",
            command=self._edit_quote,
        ).pack(
            side=tk.RIGHT,
        )

        ttk.Button(
            action_frame,
            text="Rechazar",
            command=self._reject_quote,
        ).pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )

        ttk.Button(
            action_frame,
            text="Eliminar",
            command=self._delete_quote,
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

    def _load_filter_values(self) -> None:
        try:
            proveedores = (
                self.service.listar_proveedores()
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudieron cargar los filtros",
                message=str(exc),
                parent=self,
            )
            return

        current_provider = (
            self.proveedor_filtro_var.get()
        )

        current_customs_office = (
            self.aduana_filtro_var.get()
        )

        self.proveedor_por_descripcion.clear()
        self.aduana_por_descripcion.clear()

        provider_values = [
            self.ALL_PROVIDERS
        ]

        customs_office_values = [
            self.ALL_CUSTOMS_OFFICES
        ]

        customs_office_seen: set[int] = set()

        for proveedor in proveedores:
            provider_description = (
                f"{proveedor.razon_social} "
                f"| {proveedor.cuit}"
            )

            provider_values.append(
                provider_description
            )

            self.proveedor_por_descripcion[
                provider_description
            ] = proveedor

            aduana = proveedor.aduana

            if aduana.aduana_id not in customs_office_seen:
                customs_office_seen.add(
                    aduana.aduana_id
                )

                customs_description = (
                    f"{aduana.codigo} - "
                    f"{aduana.nombre}"
                )

                customs_office_values.append(
                    customs_description
                )

                self.aduana_por_descripcion[
                    customs_description
                ] = aduana

        self.proveedor_filter.configure(
            values=provider_values
        )

        self.aduana_filter.configure(
            values=customs_office_values
        )

        if current_provider in provider_values:
            self.proveedor_filtro_var.set(
                current_provider
            )
        else:
            self.proveedor_filtro_var.set(
                self.ALL_PROVIDERS
            )

        if current_customs_office in customs_office_values:
            self.aduana_filtro_var.set(
                current_customs_office
            )
        else:
            self.aduana_filtro_var.set(
                self.ALL_CUSTOMS_OFFICES
            )

    def _selected_provider_filter(
        self,
    ) -> int | None:
        description = (
            self.proveedor_filtro_var.get()
        )

        if description == self.ALL_PROVIDERS:
            return None

        proveedor = self.proveedor_por_descripcion.get(
            description
        )

        if proveedor is None:
            return None

        return proveedor.proveedor_id

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

    def _selected_state_filter(
        self,
    ) -> str | None:
        estado = self.estado_filtro_var.get()

        if estado == self.ALL_STATES:
            return None

        return estado

    def _selected_currency_filter(
        self,
    ) -> str | None:
        moneda = self.moneda_filtro_var.get()

        if moneda == self.ALL_CURRENCIES:
            return None

        return moneda

    def _load_data(self) -> None:
        try:
            esquemas = self.service.listar(
                busqueda=self.busqueda_var.get(),
                proveedor_id=(
                    self._selected_provider_filter()
                ),
                aduana_id=(
                    self
                    ._selected_customs_office_filter()
                ),
                estado=(
                    self._selected_state_filter()
                ),
                moneda_codigo=(
                    self._selected_currency_filter()
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
                    "de esquemas.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        self._clear_table()

        for esquema in esquemas:
            proveedor = esquema.proveedor
            aduana = proveedor.aduana

            fecha_fin = (
                esquema.fecha_fin.strftime(
                    "%d/%m/%Y"
                )
                if esquema.fecha_fin
                else ""
            )

            horario = (
                "Sí"
                if esquema.utiliza_adicional_horario
                else "No"
            )

            self.table.insert(
                "",
                tk.END,
                iid=str(
                    esquema.esquema_cotizacion_id
                ),
                values=(
                    esquema.esquema_cotizacion_id,
                    proveedor.razon_social,
                    proveedor.cuit,
                    (
                        f"{aduana.codigo} - "
                        f"{aduana.nombre}"
                    ),
                    esquema.fecha_inicio.strftime(
                        "%d/%m/%Y"
                    ),
                    fecha_fin,
                    esquema.estado,
                    esquema.moneda_codigo,
                    len(esquema.zonas),
                    len(
                        esquema.adicionales_camiones
                    ),
                    horario,
                ),
            )

        cantidad = len(esquemas)

        self.status_label.configure(
            text=(
                f"{cantidad} "
                f"{'esquema' if cantidad == 1 else 'esquemas'}"
            )
        )

    def _clear_table(self) -> None:
        children = self.table.get_children()

        if children:
            self.table.delete(*children)

    def _clear_filters(self) -> None:
        self.busqueda_var.set("")

        self.proveedor_filtro_var.set(
            self.ALL_PROVIDERS
        )

        self.aduana_filtro_var.set(
            self.ALL_CUSTOMS_OFFICES
        )

        self.estado_filtro_var.set(
            self.ALL_STATES
        )

        self.moneda_filtro_var.set(
            self.ALL_CURRENCIES
        )

        self._load_data()

    def _refresh_all(self) -> None:
        self._load_filter_values()
        self._load_data()

    def _selected_id(self) -> int | None:
        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                title="Seleccionar esquema",
                message=(
                    "Selecciona un esquema "
                    "del listado."
                ),
                parent=self,
            )
            return None

        return int(selected[0])

    def _new_quote(self) -> None:
        proveedores = (
            self.service.listar_proveedores()
        )

        if not proveedores:
            messagebox.showwarning(
                title="No hay proveedores",
                message=(
                    "Antes de crear un esquema "
                    "debes registrar al menos "
                    "un proveedor."
                ),
                parent=self,
            )
            return

        dialog = EsquemaCotizacionDialog(
            parent=self,
            service=self.service,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _edit_quote(self) -> None:
        esquema_id = self._selected_id()

        if esquema_id is None:
            return

        try:
            esquema = self.service.obtener(
                esquema_id
            )

            if esquema.estado != "BORRADOR":
                messagebox.showinfo(
                    title="Esquema no editable",
                    message=(
                        "Solo los esquemas en estado "
                        "BORRADOR pueden modificarse."
                    ),
                    parent=self,
                )
                return

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo abrir",
                message=str(exc),
                parent=self,
            )
            return

        dialog = EsquemaCotizacionDialog(
            parent=self,
            service=self.service,
            esquema=esquema,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _reject_quote(self) -> None:
        esquema_id = self._selected_id()

        if esquema_id is None:
            return

        confirmed = messagebox.askyesno(
            title="Rechazar esquema",
            message=(
                "¿Deseas rechazar el esquema "
                f"{esquema_id}?\n\n"
                "Después del rechazo ya no podrá "
                "editarse ni eliminarse."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.rechazar(
                esquema_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo rechazar",
                message=str(exc),
                parent=self,
            )
            return

        self._load_data()

    def _delete_quote(self) -> None:
        esquema_id = self._selected_id()

        if esquema_id is None:
            return

        confirmed = messagebox.askyesno(
            title="Eliminar esquema",
            message=(
                "¿Deseas eliminar el esquema "
                f"{esquema_id}?\n\n"
                "Solo pueden eliminarse borradores. "
                "También se eliminarán sus datos "
                "dependientes."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.service.eliminar(
                esquema_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo eliminar",
                message=str(exc),
                parent=self,
            )
            return

        self._load_data()

        messagebox.showinfo(
            title="Esquema eliminado",
            message=(
                "El esquema se eliminó correctamente."
            ),
            parent=self,
        )

    def _complete_quote(self) -> None:
        esquema_id = self._selected_id()

        if esquema_id is None:
            return

        try:
            esquema = self.service.obtener(
                esquema_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo abrir",
                message=str(exc),
                parent=self,
            )
            return
        
        if esquema.estado != "BORRADOR":
            messagebox.showinfo(
                title="Esquema no editable",
                message=(
                    "Solo los esquemas en estado "
                    "BORRADOR pueden completarse."
                ),
                parent=self,
            )
            return
        
        window = CompletarEsquemaWindow(
            parent=self,
            esquema_cotizacion_id=esquema_id,
        )

        self.wait_window(window)
        self._refresh_all()