import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    AdicionalCamiones,
    TarifaAdicionalCamionesZona,
    Zona,
)
from validacion_honorarios.services import (
    AdicionalCamionesService,
    ApplicationError,
    EsquemaCotizacionService,
    ZonaTarifaService,
)
from validacion_honorarios.ui.monto_camiones_zona_dialog import (
    MontoCamionesZonaDialog,
)
from validacion_honorarios.ui.tramo_camiones_dialog import (
    TramoCamionesDialog,
)


class AdicionalesCamionesWindow(tk.Toplevel):
    """Gestión de tramos adicionales y tarifas por zona."""

    def __init__(
        self,
        parent: tk.Misc,
        esquema_cotizacion_id: int,
    ) -> None:
        super().__init__(parent)

        self.esquema_cotizacion_id = esquema_cotizacion_id

        self.esquema_service = EsquemaCotizacionService()
        self.adicional_service = AdicionalCamionesService()
        self.zona_service = ZonaTarifaService()

        self.esquema = self.esquema_service.obtener(
            esquema_cotizacion_id
        )

        self.tramos: list[AdicionalCamiones] = []
        self.zonas: list[Zona] = []

        self.tramo_por_id: dict[int, AdicionalCamiones] = {}
        self.zona_por_columna: dict[str, Zona] = {}

        self.selected_tramo_id: int | None = None
        self.selected_zona_id: int | None = None

        self.selected_cell_var = tk.StringVar(
            value="Ninguna celda seleccionada."
        )

        self._configure_window()
        self._build_interface()
        self._refresh_all()

        self.transient(parent)

    def _configure_window(self) -> None:
        self.title("Adicionales por camiones")
        self.geometry("1250x720")
        self.minsize(950, 580)

    def _build_interface(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()

        body = ttk.Panedwindow(
            self,
            orient=tk.HORIZONTAL,
        )
        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=14,
            pady=(0, 14),
        )

        left_panel = ttk.Frame(
            body,
            padding=12,
        )
        right_panel = ttk.Frame(
            body,
            padding=12,
        )

        body.add(left_panel, weight=1)
        body.add(right_panel, weight=4)

        self._build_tramos_panel(left_panel)
        self._build_matrix_panel(right_panel)

        footer = ttk.Frame(
            self,
            padding=(14, 0, 14, 14),
        )
        footer.grid(
            row=2,
            column=0,
            sticky=tk.EW,
        )

        ttk.Label(
            footer,
            text=(
                "Si el proveedor no establece adicionales por "
                "camiones, no es necesario crear ningún tramo."
            ),
        ).pack(side=tk.LEFT)

        ttk.Button(
            footer,
            text="Cerrar",
            command=self.destroy,
        ).pack(side=tk.RIGHT)

    def _build_header(self) -> None:
        proveedor = self.esquema.proveedor

        header = ttk.Frame(
            self,
            padding=14,
        )
        header.grid(
            row=0,
            column=0,
            sticky=tk.EW,
        )

        ttk.Label(
            header,
            text="Adicionales por camiones",
            style="SectionTitle.TLabel",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
        )

        ttk.Label(
            header,
            text=(
                f"Esquema {self.esquema.esquema_cotizacion_id}"
                f" | {proveedor.razon_social}"
                f" | {self.esquema.moneda_codigo}"
            ),
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=(8, 0),
        )

    def _build_tramos_panel(
        self,
        parent: ttk.Frame,
    ) -> None:
        ttk.Label(
            parent,
            text="Tramos",
            style="SectionTitle.TLabel",
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        ttk.Label(
            parent,
            text=(
                "Los extremos son inclusivos. "
                "Los rangos no pueden solaparse."
            ),
            wraplength=260,
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        list_frame = ttk.Frame(parent)
        list_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.tramos_list = tk.Listbox(
            list_frame,
            exportselection=False,
        )
        self.tramos_list.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tramos_list.yview,
        )
        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        self.tramos_list.configure(
            yscrollcommand=scrollbar.set,
        )

        self.tramos_list.bind(
            "<Double-1>",
            lambda _event: self._edit_tramo(),
        )

        buttons = ttk.Frame(parent)
        buttons.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        ttk.Button(
            buttons,
            text="Nuevo tramo",
            command=self._new_tramo,
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            buttons,
            text="Editar tramo",
            command=self._edit_tramo,
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            buttons,
            text="Eliminar tramo",
            command=self._delete_tramo,
        ).pack(fill=tk.X)

    def _build_matrix_panel(
        self,
        parent: ttk.Frame,
    ) -> None:
        ttk.Label(
            parent,
            text="Tarifas unitarias por zona",
            style="SectionTitle.TLabel",
        ).pack(
            anchor=tk.W,
            pady=(0, 8),
        )

        ttk.Label(
            parent,
            text=(
                "Haz clic sobre una celda para seleccionarla. "
                "Haz doble clic para crear o modificar su importe."
            ),
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        table_frame = ttk.Frame(parent)
        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.table = ttk.Treeview(
            table_frame,
            show="headings",
            selectmode="browse",
        )
        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )
        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky=tk.NS,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.table.xview,
        )
        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky=tk.EW,
        )

        self.table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.table.bind(
            "<Button-1>",
            self._table_single_click,
        )
        self.table.bind(
            "<Double-1>",
            self._table_double_click,
        )

        ttk.Label(
            parent,
            textvariable=self.selected_cell_var,
        ).pack(
            fill=tk.X,
            pady=(8, 0),
        )

        actions = ttk.Frame(parent)
        actions.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        ttk.Button(
            actions,
            text="Editar tarifa seleccionada",
            command=self._edit_selected_tarifa,
        ).pack(side=tk.LEFT)

        ttk.Button(
            actions,
            text="Quitar tarifa seleccionada",
            command=self._remove_selected_tarifa,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        ttk.Button(
            actions,
            text="Actualizar matriz",
            command=self._refresh_all,
        ).pack(side=tk.RIGHT)

        self.status_label = ttk.Label(
            parent,
            text="",
        )
        self.status_label.pack(
            fill=tk.X,
            pady=(8, 0),
        )

    def _refresh_all(self) -> None:
        try:
            self.tramos = self.adicional_service.listar_tramos(
                self.esquema_cotizacion_id
            )
            self.zonas = self.zona_service.listar_zonas(
                self.esquema_cotizacion_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudieron cargar los datos",
                message=str(exc),
                parent=self,
            )
            return

        self.tramo_por_id = {
            tramo.adicional_camiones_id: tramo
            for tramo in self.tramos
        }

        self._refresh_tramos_list()
        self._refresh_matrix()

    def _refresh_tramos_list(self) -> None:
        selected_id = self._selected_tramo_id(
            show_message=False
        )

        self.tramos_list.delete(0, tk.END)

        selected_position = None

        for index, tramo in enumerate(self.tramos):
            self.tramos_list.insert(
                tk.END,
                tramo.descripcion_rango,
            )

            if tramo.adicional_camiones_id == selected_id:
                selected_position = index

        if selected_position is not None:
            self.tramos_list.selection_set(
                selected_position
            )
            self.tramos_list.activate(
                selected_position
            )

    def _refresh_matrix(self) -> None:
        previous_tramo_id = self.selected_tramo_id
        previous_zona_id = self.selected_zona_id

        zone_columns = [
            f"zona_{zona.zona_id}"
            for zona in self.zonas
        ]

        columns = [
            "tramo",
            *zone_columns,
        ]

        self.zona_por_columna = {
            f"zona_{zona.zona_id}": zona
            for zona in self.zonas
        }

        self.table.configure(columns=columns)

        self.table.heading(
            "tramo",
            text="Tramo",
        )
        self.table.column(
            "tramo",
            width=190,
            minwidth=145,
            anchor=tk.W,
        )

        for zona in self.zonas:
            column_name = f"zona_{zona.zona_id}"

            self.table.heading(
                column_name,
                text=zona.nombre,
            )
            self.table.column(
                column_name,
                width=140,
                minwidth=105,
                anchor=tk.E,
            )

        children = self.table.get_children()
        if children:
            self.table.delete(*children)

        tariff_count = 0

        for tramo in self.tramos:
            tarifa_por_zona = {
                tarifa.zona_id: tarifa
                for tarifa in tramo.tarifas_por_zona
            }

            values = [tramo.descripcion_rango]

            for zona in self.zonas:
                tarifa = tarifa_por_zona.get(
                    zona.zona_id
                )

                if tarifa is None:
                    values.append("")
                else:
                    tariff_count += 1
                    values.append(
                        self._format_amount(
                            tarifa.monto
                        )
                    )

            self.table.insert(
                "",
                tk.END,
                iid=str(
                    tramo.adicional_camiones_id
                ),
                values=values,
            )

        self.status_label.configure(
            text=(
                f"{len(self.tramos)} tramos | "
                f"{len(self.zonas)} zonas | "
                f"{tariff_count} tarifas configuradas"
            )
        )

        selection_is_valid = (
            previous_tramo_id is not None
            and previous_zona_id is not None
            and previous_tramo_id in self.tramo_por_id
            and any(
                zona.zona_id == previous_zona_id
                for zona in self.zonas
            )
        )

        if not selection_is_valid:
            self._clear_cell_selection()
            return

        tramo = self.tramo_por_id[
            previous_tramo_id
        ]
        zona = next(
            zona
            for zona in self.zonas
            if zona.zona_id == previous_zona_id
        )

        self._set_cell_selection(
            tramo=tramo,
            zona=zona,
        )

    def _new_tramo(self) -> None:
        dialog = TramoCamionesDialog(
            parent=self,
            service=self.adicional_service,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _edit_tramo(self) -> None:
        tramo_id = self._selected_tramo_id()

        if tramo_id is None:
            return

        tramo = self.tramo_por_id.get(tramo_id)

        if tramo is None:
            return

        dialog = TramoCamionesDialog(
            parent=self,
            service=self.adicional_service,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
            tramo=tramo,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _delete_tramo(self) -> None:
        tramo_id = self._selected_tramo_id()

        if tramo_id is None:
            return

        tramo = self.tramo_por_id.get(tramo_id)

        if tramo is None:
            return

        confirmed = messagebox.askyesno(
            title="Eliminar tramo",
            message=(
                f"¿Deseas eliminar "
                f"{tramo.descripcion_rango}?\n\n"
                "También se eliminarán todas "
                "sus tarifas por zona."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.adicional_service.eliminar_tramo(
                tramo_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo eliminar",
                message=str(exc),
                parent=self,
            )
            return

        if self.selected_tramo_id == tramo_id:
            self._clear_cell_selection()

        self._refresh_all()

    def _selected_tramo_id(
        self,
        show_message: bool = True,
    ) -> int | None:
        selected = self.tramos_list.curselection()

        if not selected:
            if show_message:
                messagebox.showinfo(
                    title="Seleccionar tramo",
                    message=(
                        "Selecciona un tramo "
                        "del listado."
                    ),
                    parent=self,
                )
            return None

        position = selected[0]

        if position >= len(self.tramos):
            return None

        return self.tramos[
            position
        ].adicional_camiones_id

    def _table_single_click(
        self,
        event: tk.Event,
    ) -> None:
        selection = self._selection_from_event(
            event
        )

        if selection is None:
            self._clear_cell_selection()
            return

        tramo, zona = selection

        self._set_cell_selection(
            tramo=tramo,
            zona=zona,
        )

    def _table_double_click(
        self,
        event: tk.Event,
    ) -> None:
        selection = self._selection_from_event(
            event
        )

        if selection is None:
            return

        tramo, zona = selection

        self._set_cell_selection(
            tramo=tramo,
            zona=zona,
        )

        self._open_tarifa_dialog(
            tramo=tramo,
            zona=zona,
        )

    def _selection_from_event(
        self,
        event: tk.Event,
    ) -> tuple[AdicionalCamiones, Zona] | None:
        region = self.table.identify_region(
            event.x,
            event.y,
        )

        if region != "cell":
            return None

        row_id = self.table.identify_row(
            event.y
        )
        column_id = self.table.identify_column(
            event.x
        )

        if not row_id:
            return None

        try:
            tramo_id = int(row_id)
            column_number = int(
                column_id.removeprefix("#")
            )
        except ValueError:
            return None

        tramo = self.tramo_por_id.get(
            tramo_id
        )

        if tramo is None:
            return None

        columns = list(self.table["columns"])
        column_index = column_number - 1

        if (
            column_index < 0
            or column_index >= len(columns)
        ):
            return None

        column_name = columns[column_index]

        if column_name == "tramo":
            return None

        zona = self.zona_por_columna.get(
            column_name
        )

        if zona is None:
            return None

        return tramo, zona

    def _set_cell_selection(
        self,
        tramo: AdicionalCamiones,
        zona: Zona,
    ) -> None:
        self.selected_tramo_id = (
            tramo.adicional_camiones_id
        )
        self.selected_zona_id = zona.zona_id

        self.table.selection_set(
            str(tramo.adicional_camiones_id)
        )
        self.table.focus(
            str(tramo.adicional_camiones_id)
        )

        tarifa = self._find_tarifa(
            tramo=tramo,
            zona=zona,
        )

        valor = (
            self._format_amount(tarifa.monto)
            if tarifa is not None
            else "sin tarifa"
        )

        self.selected_cell_var.set(
            f"Celda seleccionada: "
            f"{tramo.descripcion_rango} × "
            f"{zona.nombre} ({valor})"
        )

    def _current_selection(
        self,
    ) -> tuple[AdicionalCamiones, Zona] | None:
        if (
            self.selected_tramo_id is None
            or self.selected_zona_id is None
        ):
            messagebox.showinfo(
                title="Seleccionar tarifa",
                message=(
                    "Haz clic sobre una celda "
                    "de tramo y zona."
                ),
                parent=self,
            )
            return None

        tramo = self.tramo_por_id.get(
            self.selected_tramo_id
        )
        zona = next(
            (
                zona
                for zona in self.zonas
                if zona.zona_id
                == self.selected_zona_id
            ),
            None,
        )

        if tramo is None or zona is None:
            self._clear_cell_selection()
            return None

        return tramo, zona

    def _edit_selected_tarifa(self) -> None:
        selection = self._current_selection()

        if selection is None:
            return

        tramo, zona = selection

        self._open_tarifa_dialog(
            tramo=tramo,
            zona=zona,
        )

    def _remove_selected_tarifa(self) -> None:
        selection = self._current_selection()

        if selection is None:
            return

        tramo, zona = selection

        tarifa = self._find_tarifa(
            tramo=tramo,
            zona=zona,
        )

        if tarifa is None:
            messagebox.showinfo(
                title="Sin tarifa",
                message=(
                    "La combinación seleccionada "
                    "no tiene una tarifa cargada."
                ),
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            title="Quitar tarifa",
            message=(
                "¿Deseas quitar la tarifa de "
                f"{tramo.descripcion_rango} para "
                f"la zona {zona.nombre}?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.adicional_service.eliminar_tarifa(
                esquema_cotizacion_id=(
                    self.esquema_cotizacion_id
                ),
                adicional_camiones_id=(
                    tramo.adicional_camiones_id
                ),
                zona_id=zona.zona_id,
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo quitar",
                message=str(exc),
                parent=self,
            )
            return

        self._refresh_all()

    def _open_tarifa_dialog(
        self,
        tramo: AdicionalCamiones,
        zona: Zona,
    ) -> None:
        tarifa = self._find_tarifa(
            tramo=tramo,
            zona=zona,
        )

        dialog = MontoCamionesZonaDialog(
            parent=self,
            service=self.adicional_service,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
            adicional_camiones_id=(
                tramo.adicional_camiones_id
            ),
            zona_id=zona.zona_id,
            tramo_descripcion=(
                tramo.descripcion_rango
            ),
            zona_nombre=zona.nombre,
            moneda_codigo=(
                self.esquema.moneda_codigo
            ),
            monto_actual=(
                tarifa.monto
                if tarifa is not None
                else None
            ),
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _clear_cell_selection(self) -> None:
        self.selected_tramo_id = None
        self.selected_zona_id = None

        self.selected_cell_var.set(
            "Ninguna celda seleccionada."
        )

    @staticmethod
    def _find_tarifa(
        tramo: AdicionalCamiones,
        zona: Zona,
    ) -> TarifaAdicionalCamionesZona | None:
        for tarifa in tramo.tarifas_por_zona:
            if tarifa.zona_id == zona.zona_id:
                return tarifa

        return None

    @staticmethod
    def _format_amount(
        amount: Decimal,
    ) -> str:
        return (
            f"{amount:,.2f}"
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )
