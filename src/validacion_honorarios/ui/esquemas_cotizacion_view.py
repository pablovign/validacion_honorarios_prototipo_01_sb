import tkinter as tk
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import Aduana, Proveedor
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
)
from validacion_honorarios.ui.esquema_wizard_window import (
    EsquemaWizardWindow,
)
from validacion_honorarios.ui.resumen_esquema_window import (
    ResumenEsquemaWindow,
)


class EsquemasCotizacionView(ttk.Frame):
    """Listado y acceso al wizard de esquemas de cotización."""

    ALL_PROVIDERS = "Todos los proveedores"
    ALL_CUSTOMS = "Todas las aduanas"
    ALL_STATES = "Todos los estados"
    ALL_CURRENCIES = "Todas las monedas"

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=20)

        self.service = EsquemaCotizacionService()
        self.search_var = tk.StringVar()
        self.provider_filter_var = tk.StringVar(value=self.ALL_PROVIDERS)
        self.customs_filter_var = tk.StringVar(value=self.ALL_CUSTOMS)
        self.state_filter_var = tk.StringVar(value=self.ALL_STATES)
        self.currency_filter_var = tk.StringVar(value=self.ALL_CURRENCIES)
        self.provider_by_label: dict[str, Proveedor] = {}
        self.customs_by_label: dict[str, Aduana] = {}

        self._build_interface()
        self._load_filter_values()
        self._load_data()

    def _build_interface(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 14))

        ttk.Label(
            header,
            text="Esquemas de cotización",
            style="SectionTitle.TLabel",
        ).pack(side=tk.LEFT)

        ttk.Button(
            header,
            text="Nuevo esquema",
            command=self._new_quote,
        ).pack(side=tk.RIGHT)

        ttk.Label(
            self,
            text=(
                "Los borradores se crean y completan mediante un único "
                "asistente. Los esquemas rechazados o aprobados se consultan "
                "desde su vista general."
            ),
            wraplength=950,
        ).pack(fill=tk.X, anchor=tk.W, pady=(0, 14))

        filters = ttk.LabelFrame(self, text="Filtros", padding=12)
        filters.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(filters, text="Buscar").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(filters, text="Proveedor").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(filters, text="Aduana").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        ttk.Label(filters, text="Estado").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(filters, text="Moneda").grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))

        search_entry = ttk.Entry(filters, textvariable=self.search_var)
        search_entry.grid(row=1, column=0, sticky=tk.EW, pady=(4, 0))
        search_entry.bind("<Return>", lambda _event: self._load_data())

        self.provider_filter = ttk.Combobox(
            filters,
            textvariable=self.provider_filter_var,
            state="readonly",
        )
        self.provider_filter.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=(4, 0))

        self.customs_filter = ttk.Combobox(
            filters,
            textvariable=self.customs_filter_var,
            state="readonly",
        )
        self.customs_filter.grid(row=1, column=2, sticky=tk.EW, padx=(10, 0), pady=(4, 0))

        self.state_filter = ttk.Combobox(
            filters,
            textvariable=self.state_filter_var,
            state="readonly",
            values=(self.ALL_STATES, "BORRADOR", "APROBADO", "RECHAZADO"),
        )
        self.state_filter.grid(row=3, column=0, sticky=tk.EW, pady=(4, 0))

        self.currency_filter = ttk.Combobox(
            filters,
            textvariable=self.currency_filter_var,
            state="readonly",
            values=(self.ALL_CURRENCIES, "ARS", "USD"),
        )
        self.currency_filter.grid(row=3, column=1, sticky=tk.EW, padx=(10, 0), pady=(4, 0))

        buttons = ttk.Frame(filters)
        buttons.grid(row=3, column=2, sticky=tk.E, padx=(10, 0), pady=(4, 0))
        ttk.Button(buttons, text="Aplicar", command=self._load_data).pack(side=tk.LEFT)
        ttk.Button(buttons, text="Limpiar", command=self._clear_filters).pack(side=tk.LEFT, padx=(8, 0))

        for column in range(3):
            filters.columnconfigure(column, weight=1)

        for combo in (
            self.provider_filter,
            self.customs_filter,
            self.state_filter,
            self.currency_filter,
        ):
            combo.bind("<<ComboboxSelected>>", lambda _event: self._load_data())

        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = (
            "id",
            "proveedor",
            "cuit",
            "aduana",
            "inicio",
            "fin",
            "estado",
            "moneda",
            "zonas",
            "tramos",
            "horario",
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.bind("<Double-1>", lambda _event: self._primary_action())

        headings = {
            "id": "ID",
            "proveedor": "Proveedor",
            "cuit": "CUIT",
            "aduana": "Aduana",
            "inicio": "Inicio",
            "fin": "Fin",
            "estado": "Estado",
            "moneda": "Moneda",
            "zonas": "Zonas",
            "tramos": "Tramos",
            "horario": "Horario",
        }

        for column, heading in headings.items():
            self.table.heading(column, text=heading)

        widths = {
            "id": 65,
            "proveedor": 240,
            "cuit": 115,
            "aduana": 170,
            "inicio": 95,
            "fin": 95,
            "estado": 100,
            "moneda": 75,
            "zonas": 65,
            "tramos": 70,
            "horario": 80,
        }

        for column, width in widths.items():
            anchor = tk.W if column in ("proveedor", "aduana") else tk.CENTER
            self.table.column(column, width=width, anchor=anchor, stretch=column in ("proveedor", "aduana"))

        ybar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        ybar.grid(row=0, column=1, sticky="ns")
        xbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        xbar.grid(row=1, column=0, sticky="ew")
        self.table.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        actions = ttk.Frame(self)
        actions.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(actions, text="Actualizar", command=self._refresh_all).pack(side=tk.LEFT)
        ttk.Button(actions, text="Continuar esquema", command=self._continue_quote).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Ver resumen", command=self._show_summary).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(actions, text="Editar cabecera", command=self._edit_quote).pack(side=tk.RIGHT)
        ttk.Button(actions, text="Rechazar", command=self._reject_quote).pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(actions, text="Eliminar", command=self._delete_quote).pack(side=tk.RIGHT, padx=(0, 8))

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def _load_filter_values(self) -> None:
        try:
            providers = self.service.listar_proveedores()
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudieron cargar los filtros", message=str(exc), parent=self)
            return

        current_provider = self.provider_filter_var.get()
        current_customs = self.customs_filter_var.get()
        self.provider_by_label.clear()
        self.customs_by_label.clear()

        provider_values = [self.ALL_PROVIDERS]
        customs_values = [self.ALL_CUSTOMS]
        seen_customs = set()

        for provider in providers:
            provider_label = f"{provider.razon_social} | {provider.cuit}"
            provider_values.append(provider_label)
            self.provider_by_label[provider_label] = provider

            customs = provider.aduana
            if customs.aduana_id not in seen_customs:
                seen_customs.add(customs.aduana_id)
                customs_label = f"{customs.codigo} - {customs.nombre}"
                customs_values.append(customs_label)
                self.customs_by_label[customs_label] = customs

        self.provider_filter.configure(values=provider_values)
        self.customs_filter.configure(values=customs_values)
        self.provider_filter_var.set(current_provider if current_provider in provider_values else self.ALL_PROVIDERS)
        self.customs_filter_var.set(current_customs if current_customs in customs_values else self.ALL_CUSTOMS)

    def _load_data(self) -> None:
        provider = self.provider_by_label.get(self.provider_filter_var.get())
        customs = self.customs_by_label.get(self.customs_filter_var.get())
        state = self.state_filter_var.get()
        currency = self.currency_filter_var.get()

        try:
            schemes = self.service.listar(
                busqueda=self.search_var.get(),
                proveedor_id=provider.proveedor_id if provider else None,
                aduana_id=customs.aduana_id if customs else None,
                estado=None if state == self.ALL_STATES else state,
                moneda_codigo=None if currency == self.ALL_CURRENCIES else currency,
            )
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo consultar", message=str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(title="Error inesperado", message=f"No se pudo recuperar el listado.\n\n{exc}", parent=self)
            return

        children = self.table.get_children()
        if children:
            self.table.delete(*children)

        for scheme in schemes:
            provider = scheme.proveedor
            customs = provider.aduana
            self.table.insert(
                "",
                tk.END,
                iid=str(scheme.esquema_cotizacion_id),
                values=(
                    scheme.esquema_cotizacion_id,
                    provider.razon_social,
                    provider.cuit,
                    f"{customs.codigo} - {customs.nombre}",
                    scheme.fecha_inicio.strftime("%d/%m/%Y"),
                    scheme.fecha_fin.strftime("%d/%m/%Y") if scheme.fecha_fin else "",
                    scheme.estado,
                    scheme.moneda_codigo,
                    len(scheme.zonas),
                    len(scheme.adicionales_camiones),
                    "Sí" if scheme.tarifas_adicionales_dia_hora else "No",
                ),
            )

        count = len(schemes)
        self.status_label.configure(text=f"{count} {'esquema' if count == 1 else 'esquemas'}")

    def _clear_filters(self) -> None:
        self.search_var.set("")
        self.provider_filter_var.set(self.ALL_PROVIDERS)
        self.customs_filter_var.set(self.ALL_CUSTOMS)
        self.state_filter_var.set(self.ALL_STATES)
        self.currency_filter_var.set(self.ALL_CURRENCIES)
        self._load_data()

    def _refresh_all(self) -> None:
        self._load_filter_values()
        self._load_data()

    def _selected_id(self) -> int | None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo(title="Seleccionar esquema", message="Selecciona un esquema del listado.", parent=self)
            return None
        return int(selected[0])

    def _selected_scheme(self):
        scheme_id = self._selected_id()
        if scheme_id is None:
            return None
        try:
            return self.service.obtener(scheme_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo abrir", message=str(exc), parent=self)
            return None

    def _new_quote(self) -> None:
        providers = self.service.listar_proveedores()
        if not providers:
            messagebox.showwarning(title="No hay proveedores", message="Registra al menos un proveedor antes de crear un esquema.", parent=self)
            return

        wizard = EsquemaWizardWindow(parent=self)
        self.wait_window(wizard)
        if wizard.resultado_guardado:
            self._refresh_all()

    def _continue_quote(self) -> None:
        scheme = self._selected_scheme()
        if scheme is None:
            return
        if scheme.estado != "BORRADOR":
            messagebox.showinfo(
                title="Esquema de solo lectura",
                message="Solo los esquemas BORRADOR pueden continuar en el asistente. Usa Ver resumen.",
                parent=self,
            )
            return
        wizard = EsquemaWizardWindow(parent=self, esquema_cotizacion_id=scheme.esquema_cotizacion_id)
        self.wait_window(wizard)
        self._refresh_all()

    def _primary_action(self) -> None:
        scheme = self._selected_scheme()
        if scheme is None:
            return
        if scheme.estado == "BORRADOR":
            self._continue_quote()
        else:
            self._show_summary()

    def _show_summary(self) -> None:
        scheme_id = self._selected_id()
        if scheme_id is None:
            return
        window = ResumenEsquemaWindow(parent=self, esquema_cotizacion_id=scheme_id)
        self.wait_window(window)

    def _edit_quote(self) -> None:
        scheme = self._selected_scheme()
        if scheme is None:
            return
        if scheme.estado != "BORRADOR":
            messagebox.showinfo(title="Esquema no editable", message="Solo los borradores pueden editarse.", parent=self)
            return
        wizard = EsquemaWizardWindow(parent=self, esquema_cotizacion_id=scheme.esquema_cotizacion_id)
        wizard._show_step(0)
        self.wait_window(wizard)
        self._refresh_all()

    def _reject_quote(self) -> None:
        scheme = self._selected_scheme()
        if scheme is None:
            return
        if not messagebox.askyesno(title="Rechazar esquema", message=f"¿Rechazar el esquema {scheme.esquema_cotizacion_id}?", parent=self):
            return
        try:
            self.service.rechazar(scheme.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo rechazar", message=str(exc), parent=self)
            return
        self._load_data()

    def _delete_quote(self) -> None:
        scheme = self._selected_scheme()
        if scheme is None:
            return
        if not messagebox.askyesno(title="Eliminar esquema", message=f"¿Eliminar el borrador {scheme.esquema_cotizacion_id} y todos sus datos?", parent=self):
            return
        try:
            self.service.eliminar(scheme.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self)
            return
        self._refresh_all()
