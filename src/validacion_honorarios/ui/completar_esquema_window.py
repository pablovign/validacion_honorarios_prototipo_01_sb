import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    CanalSelectividad,
    EsquemaCotizacion,
    TarifaZonaCanalSelectividad,
    Zona,
)
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
    ZonaTarifaService,
)
from validacion_honorarios.ui.monto_tarifa_dialog import (
    MontoTarifaDialog,
)
from validacion_honorarios.ui.zona_dialog import (
    ZonaDialog,
)
from validacion_honorarios.ui.adicionales_camiones_window import (
    AdicionalesCamionesWindow,
)
from validacion_honorarios.ui.adicionales_dia_hora_window import (
    AdicionalesDiaHoraWindow,
)
from validacion_honorarios.ui.resumen_esquema_window import (
    ResumenEsquemaWindow,
)

class CompletarEsquemaWindow(tk.Toplevel):
    """Edición de los componentes internos de un esquema."""

    def __init__(
        self,
        parent: tk.Misc,
        esquema_cotizacion_id: int,
    ) -> None:
        super().__init__(parent)

        self.esquema_service = (
            EsquemaCotizacionService()
        )
        self.zona_service = ZonaTarifaService()

        self.esquema_cotizacion_id = (
            esquema_cotizacion_id
        )

        self.esquema: EsquemaCotizacion | None = None
        self.zonas: list[Zona] = []
        self.canales: list[CanalSelectividad] = []

        self.zona_por_id: dict[int, Zona] = {}

        self.canal_por_columna: dict[
            str,
            CanalSelectividad,
        ] = {}

        # Treeview selecciona filas, no celdas.
        # Guardamos explícitamente la zona y el canal
        # correspondientes a la celda pulsada.
        self.selected_zone_id: int | None = None

        self.selected_channel_id: int | None = (
            None
        )

        self.selected_cell_var = tk.StringVar(
            value="Ninguna celda seleccionada."
        )

        self._configure_window()
        self._load_reference_data()
        self._build_interface()
        self._refresh_all()

        self.transient(parent)

    def _configure_window(self) -> None:
        self.title(
            "Completar esquema de cotización"
        )

        self.geometry("1450x820")
        self.minsize(1100, 650)

    def _load_reference_data(self) -> None:
        self.esquema = (
            self.esquema_service.obtener(
                self.esquema_cotizacion_id
            )
        )

        self.canales = (
            self.zona_service.listar_canales()
        )

    def _build_interface(self) -> None:
        self.columnconfigure(
            0,
            weight=1,
        )

        self.rowconfigure(
            1,
            weight=1,
        )

        self._build_header()

        self.paned_window = ttk.Panedwindow(
            self,
            orient=tk.HORIZONTAL,
        )

        self.paned_window.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=14,
            pady=(0, 14),
        )

        self.zone_panel = ttk.Frame(
            self.paned_window,
            padding=12,
        )

        self.tariff_panel = ttk.Frame(
            self.paned_window,
            padding=12,
        )

        self.document_panel = ttk.Frame(
            self.paned_window,
            padding=12,
        )

        self.paned_window.add(
            self.zone_panel,
            weight=1,
        )

        self.paned_window.add(
            self.tariff_panel,
            weight=4,
        )

        self.paned_window.add(
            self.document_panel,
            weight=2,
        )

        self._build_zone_panel()
        self._build_tariff_panel()
        self._build_document_panel()

        footer = ttk.Frame(
            self,
            padding=(14, 0, 14, 14),
        )

        footer.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        ttk.Button(
            footer,
            text="Adicionales por día y hora",
            command=self._open_day_hour_additions,
        ).pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )

        ttk.Button(
            footer,
            text="Adicionales por camiones",
            command=self._open_truck_additions,
        ).pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )

        ttk.Button(
            footer,
            text="Vista general",
            command=self._open_summary,
        ).pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )

        ttk.Button(
            footer,
            text="Cerrar",
        command=self.destroy,
        ).pack(
            side=tk.RIGHT,
        )
        

        ttk.Label(
            footer,
            text=(
                "Los cambios se guardan al confirmar "
                "cada zona o tarifa."
            ),
        ).pack(
            side=tk.LEFT,
        )

    def _build_header(self) -> None:
        if self.esquema is None:
            return

        proveedor = self.esquema.proveedor
        aduana = proveedor.aduana

        header = ttk.Frame(
            self,
            padding=14,
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        ttk.Label(
            header,
            text=(
                f"Esquema "
                f"{self.esquema.esquema_cotizacion_id}"
            ),
            style="SectionTitle.TLabel",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
        )

        ttk.Label(
            header,
            text=(
                f"Proveedor: "
                f"{proveedor.razon_social}"
            ),
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=(8, 0),
        )

        ttk.Label(
            header,
            text=(
                f"Aduana: {aduana.codigo} - "
                f"{aduana.nombre}"
            ),
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(3, 0),
        )

        ttk.Label(
            header,
            text=(
                f"Moneda: "
                f"{self.esquema.moneda_codigo}"
            ),
        ).grid(
            row=1,
            column=1,
            sticky=tk.W,
            padx=(30, 0),
            pady=(8, 0),
        )

        ttk.Label(
            header,
            text=(
                f"Inicio: "
                f"{self.esquema.fecha_inicio.strftime('%d/%m/%Y')}"
            ),
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=(30, 0),
            pady=(3, 0),
        )

        ttk.Label(
            header,
            text=(
                f"Estado: {self.esquema.estado}"
            ),
        ).grid(
            row=1,
            column=2,
            sticky=tk.W,
            padx=(30, 0),
            pady=(8, 0),
        )

        header.columnconfigure(
            0,
            weight=1,
        )

    def _build_zone_panel(self) -> None:
        ttk.Label(
            self.zone_panel,
            text="Zonas",
            style="SectionTitle.TLabel",
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        ttk.Label(
            self.zone_panel,
            text=(
                "Crea GENERAL si el proveedor "
                "no diferencia zonas."
            ),
            wraplength=250,
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        list_frame = ttk.Frame(
            self.zone_panel
        )

        list_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.zone_list = tk.Listbox(
            list_frame,
            exportselection=False,
        )

        self.zone_list.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.zone_list.yview,
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        self.zone_list.configure(
            yscrollcommand=scrollbar.set,
        )

        self.zone_list.bind(
            "<Double-1>",
            lambda _event: self._edit_zone(),
        )

        buttons = ttk.Frame(
            self.zone_panel
        )

        buttons.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        ttk.Button(
            buttons,
            text="Nueva",
            command=self._new_zone,
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            buttons,
            text="Editar",
            command=self._edit_zone,
        ).pack(
            fill=tk.X,
            pady=(0, 6),
        )

        ttk.Button(
            buttons,
            text="Eliminar",
            command=self._delete_zone,
        ).pack(
            fill=tk.X,
        )

    def _build_tariff_panel(self) -> None:
        ttk.Label(
            self.tariff_panel,
            text="Tarifas por zona y canal",
            style="SectionTitle.TLabel",
        ).pack(
            anchor=tk.W,
            pady=(0, 8),
        )

        ttk.Label(
            self.tariff_panel,
            text=(
                "Haz clic sobre una celda para "
                "seleccionarla. Haz doble clic para "
                "crear o modificar su importe."
            ),
            wraplength=700,
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        table_container = ttk.Frame(
            self.tariff_panel
        )

        table_container.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.tariff_table = ttk.Treeview(
            table_container,
            show="headings",
            selectmode="browse",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient=tk.VERTICAL,
            command=self.tariff_table.yview,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient=tk.HORIZONTAL,
            command=self.tariff_table.xview,
        )

        self.tariff_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.tariff_table.grid(
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

        table_container.rowconfigure(
            0,
            weight=1,
        )

        table_container.columnconfigure(
            0,
            weight=1,
        )

        self.tariff_table.bind(
            "<Button-1>",
            self._table_single_click,
        )

        self.tariff_table.bind(
            "<Double-1>",
            self._table_double_click,
        )

        selected_cell_label = ttk.Label(
            self.tariff_panel,
            textvariable=self.selected_cell_var,
        )

        selected_cell_label.pack(
            fill=tk.X,
            pady=(8, 0),
        )

        action_frame = ttk.Frame(
            self.tariff_panel
        )

        action_frame.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        ttk.Button(
            action_frame,
            text="Editar tarifa seleccionada",
            command=self._edit_selected_tariff,
        ).pack(
            side=tk.LEFT,
        )

        ttk.Button(
            action_frame,
            text="Quitar tarifa seleccionada",
            command=self._remove_selected_tariff,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        ttk.Button(
            action_frame,
            text="Actualizar matriz",
            command=self._refresh_all,
        ).pack(
            side=tk.RIGHT,
        )

        self.matrix_status = ttk.Label(
            self.tariff_panel,
            text="",
        )

        self.matrix_status.pack(
            fill=tk.X,
            pady=(8, 0),
        )

    def _build_document_panel(self) -> None:
        ttk.Label(
            self.document_panel,
            text="Documento de referencia",
            style="SectionTitle.TLabel",
        ).pack(
            anchor=tk.W,
            pady=(0, 10),
        )

        placeholder = ttk.LabelFrame(
            self.document_panel,
            text="Panel documental",
            padding=18,
        )

        placeholder.pack(
            fill=tk.BOTH,
            expand=True,
        )

        ttk.Label(
            placeholder,
            text=(
                "Aquí se mostrará el PDF, Excel o "
                "Word enviado por el proveedor."
            ),
            justify=tk.CENTER,
            wraplength=260,
        ).pack(
            expand=True,
            pady=(20, 8),
        )

        ttk.Label(
            placeholder,
            text=(
                "La asociación, copia y visualización "
                "del archivo se incorporará en el "
                "siguiente componente del MVP."
            ),
            justify=tk.CENTER,
            wraplength=260,
            foreground="#555555",
        ).pack(
            pady=(0, 20),
        )

    def _refresh_all(self) -> None:
        try:
            self.zonas = (
                self.zona_service.listar_zonas(
                    self.esquema_cotizacion_id
                )
            )

            self.canales = (
                self.zona_service.listar_canales()
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudieron cargar los datos",
                message=str(exc),
                parent=self,
            )
            return

        self.zona_por_id = {
            zona.zona_id: zona
            for zona in self.zonas
        }

        self._refresh_zone_list()
        self._refresh_tariff_matrix()

    def _refresh_zone_list(self) -> None:
        selected_id = self._selected_zone_id(
            show_message=False
        )

        self.zone_list.delete(
            0,
            tk.END,
        )

        selected_position = None

        for index, zona in enumerate(
            self.zonas
        ):
            self.zone_list.insert(
                tk.END,
                zona.nombre,
            )

            if zona.zona_id == selected_id:
                selected_position = index

        if selected_position is not None:
            self.zone_list.selection_set(
                selected_position
            )

            self.zone_list.activate(
                selected_position
            )

    def _refresh_tariff_matrix(self) -> None:
        previous_zone_id = (
            self.selected_zone_id
        )

        previous_channel_id = (
            self.selected_channel_id
        )

        channel_columns = [
            (
                f"canal_"
                f"{canal.canal_selectividad_id}"
            )
            for canal in self.canales
        ]

        columns = [
            "zona",
            *channel_columns,
        ]

        self.canal_por_columna = {
            (
                f"canal_"
                f"{canal.canal_selectividad_id}"
            ): canal
            for canal in self.canales
        }

        self.tariff_table.configure(
            columns=columns,
        )

        self.tariff_table.heading(
            "zona",
            text="Zona",
        )

        self.tariff_table.column(
            "zona",
            width=180,
            minwidth=130,
            anchor=tk.W,
            stretch=True,
        )

        for canal in self.canales:
            column_name = (
                f"canal_"
                f"{canal.canal_selectividad_id}"
            )

            self.tariff_table.heading(
                column_name,
                text=canal.nombre,
            )

            self.tariff_table.column(
                column_name,
                width=130,
                minwidth=100,
                anchor=tk.E,
            )

        children = (
            self.tariff_table.get_children()
        )

        if children:
            self.tariff_table.delete(
                *children
            )

        tariff_count = 0

        for zona in self.zonas:
            tariff_by_channel = {
                tarifa.canal_selectividad_id: tarifa
                for tarifa in zona.tarifas_por_canal
            }

            values = [
                zona.nombre,
            ]

            for canal in self.canales:
                tarifa = tariff_by_channel.get(
                    canal.canal_selectividad_id
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

            self.tariff_table.insert(
                "",
                tk.END,
                iid=str(zona.zona_id),
                values=values,
            )

        self.matrix_status.configure(
            text=(
                f"{len(self.zonas)} zonas | "
                f"{len(self.canales)} canales | "
                f"{tariff_count} tarifas configuradas"
            )
        )

        selection_is_valid = (
            previous_zone_id is not None
            and previous_channel_id is not None
            and previous_zone_id
            in self.zona_por_id
            and any(
                (
                    canal.canal_selectividad_id
                    == previous_channel_id
                )
                for canal in self.canales
            )
        )

        if not selection_is_valid:
            self._clear_cell_selection()
            return

        self.selected_zone_id = (
            previous_zone_id
        )

        self.selected_channel_id = (
            previous_channel_id
        )

        zona = self.zona_por_id[
            previous_zone_id
        ]

        canal = next(
            canal
            for canal in self.canales
            if (
                canal.canal_selectividad_id
                == previous_channel_id
            )
        )

        tarifa = self._find_tariff(
            zona=zona,
            canal=canal,
        )

        valor = (
            self._format_amount(
                tarifa.monto
            )
            if tarifa is not None
            else "sin tarifa"
        )

        self.selected_cell_var.set(
            f"Celda seleccionada: "
            f"{zona.nombre} × {canal.nombre} "
            f"({valor})"
        )

        self.tariff_table.selection_set(
            str(previous_zone_id)
        )

        self.tariff_table.focus(
            str(previous_zone_id)
        )

    def _new_zone(self) -> None:
        dialog = ZonaDialog(
            parent=self,
            service=self.zona_service,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _edit_zone(self) -> None:
        zona_id = self._selected_zone_id()

        if zona_id is None:
            return

        zona = self.zona_por_id.get(
            zona_id
        )

        if zona is None:
            return

        dialog = ZonaDialog(
            parent=self,
            service=self.zona_service,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
            zona=zona,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _delete_zone(self) -> None:
        zona_id = self._selected_zone_id()

        if zona_id is None:
            return

        zona = self.zona_por_id.get(
            zona_id
        )

        if zona is None:
            return

        confirmed = messagebox.askyesno(
            title="Eliminar zona",
            message=(
                f"¿Deseas eliminar la zona "
                f"{zona.nombre}?\n\n"
                "También se eliminarán sus tarifas "
                "por canal y las relaciones "
                "dependientes del esquema."
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.zona_service.eliminar_zona(
                zona_id
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo eliminar",
                message=str(exc),
                parent=self,
            )
            return

        if self.selected_zone_id == zona_id:
            self._clear_cell_selection()

        self._refresh_all()

    def _selected_zone_id(
        self,
        show_message: bool = True,
    ) -> int | None:
        selected = self.zone_list.curselection()

        if not selected:
            if show_message:
                messagebox.showinfo(
                    title="Seleccionar zona",
                    message=(
                        "Selecciona una zona "
                        "del listado."
                    ),
                    parent=self,
                )

            return None

        position = selected[0]

        if position >= len(self.zonas):
            return None

        return self.zonas[
            position
        ].zona_id

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

        zona, canal = selection

        self._set_cell_selection(
            zona=zona,
            canal=canal,
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

        zona, canal = selection

        self._set_cell_selection(
            zona=zona,
            canal=canal,
        )

        self._open_tariff_dialog(
            zona=zona,
            canal=canal,
        )

    def _selection_from_event(
        self,
        event: tk.Event,
    ) -> tuple[
        Zona,
        CanalSelectividad,
    ] | None:
        region = self.tariff_table.identify_region(
            event.x,
            event.y,
        )

        if region != "cell":
            return None

        row_id = self.tariff_table.identify_row(
            event.y
        )

        column_id = (
            self.tariff_table.identify_column(
                event.x
            )
        )

        return self._matrix_selection_from_ids(
            row_id=row_id,
            column_id=column_id,
            show_message=False,
        )

    def _set_cell_selection(
        self,
        zona: Zona,
        canal: CanalSelectividad,
    ) -> None:
        self.selected_zone_id = zona.zona_id

        self.selected_channel_id = (
            canal.canal_selectividad_id
        )

        self.tariff_table.selection_set(
            str(zona.zona_id)
        )

        self.tariff_table.focus(
            str(zona.zona_id)
        )

        tarifa = self._find_tariff(
            zona=zona,
            canal=canal,
        )

        amount_description = (
            self._format_amount(
                tarifa.monto
            )
            if tarifa is not None
            else "sin tarifa"
        )

        self.selected_cell_var.set(
            f"Celda seleccionada: "
            f"{zona.nombre} × {canal.nombre} "
            f"({amount_description})"
        )

    def _edit_selected_tariff(self) -> None:
        selection = (
            self._current_matrix_selection()
        )

        if selection is None:
            return

        zona, canal = selection

        self._open_tariff_dialog(
            zona=zona,
            canal=canal,
        )

    def _remove_selected_tariff(self) -> None:
        selection = (
            self._current_matrix_selection()
        )

        if selection is None:
            return

        zona, canal = selection

        tarifa = self._find_tariff(
            zona=zona,
            canal=canal,
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
                f"¿Deseas quitar la tarifa de "
                f"{zona.nombre} para el canal "
                f"{canal.nombre}?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.zona_service.eliminar_tarifa(
                esquema_cotizacion_id=(
                    self.esquema_cotizacion_id
                ),
                zona_id=zona.zona_id,
                canal_selectividad_id=(
                    canal.canal_selectividad_id
                ),
            )

        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo quitar",
                message=str(exc),
                parent=self,
            )
            return

        self._refresh_all()

    def _current_matrix_selection(
        self,
    ) -> tuple[
        Zona,
        CanalSelectividad,
    ] | None:
        if (
            self.selected_zone_id is None
            or self.selected_channel_id is None
        ):
            messagebox.showinfo(
                title="Seleccionar tarifa",
                message=(
                    "Haz clic sobre una celda "
                    "correspondiente a un canal."
                ),
                parent=self,
            )
            return None

        zona = self.zona_por_id.get(
            self.selected_zone_id
        )

        canal = next(
            (
                item
                for item in self.canales
                if (
                    item.canal_selectividad_id
                    == self.selected_channel_id
                )
            ),
            None,
        )

        if zona is None or canal is None:
            self._clear_cell_selection()

            messagebox.showwarning(
                title="Selección no disponible",
                message=(
                    "La zona o el canal seleccionado "
                    "ya no está disponible."
                ),
                parent=self,
            )

            return None

        return zona, canal

    def _matrix_selection_from_ids(
        self,
        row_id: str,
        column_id: str,
        show_message: bool = True,
    ) -> tuple[
        Zona,
        CanalSelectividad,
    ] | None:
        if not row_id:
            return None

        try:
            zona_id = int(row_id)
        except ValueError:
            return None

        zona = self.zona_por_id.get(
            zona_id
        )

        if zona is None:
            return None

        try:
            column_number = int(
                column_id.removeprefix("#")
            )
        except ValueError:
            return None

        columns = list(
            self.tariff_table["columns"]
        )

        column_index = column_number - 1

        if (
            column_index < 0
            or column_index >= len(columns)
        ):
            return None

        column_name = columns[
            column_index
        ]

        if column_name == "zona":
            if show_message:
                messagebox.showinfo(
                    title="Seleccionar canal",
                    message=(
                        "La primera columna identifica "
                        "la zona. Selecciona una celda "
                        "de un canal."
                    ),
                    parent=self,
                )

            return None

        canal = self.canal_por_columna.get(
            column_name
        )

        if canal is None:
            return None

        return zona, canal

    def _clear_cell_selection(self) -> None:
        self.selected_zone_id = None
        self.selected_channel_id = None

        self.selected_cell_var.set(
            "Ninguna celda seleccionada."
        )

    def _open_tariff_dialog(
        self,
        zona: Zona,
        canal: CanalSelectividad,
    ) -> None:
        if self.esquema is None:
            return

        tarifa = self._find_tariff(
            zona=zona,
            canal=canal,
        )

        dialog = MontoTarifaDialog(
            parent=self,
            service=self.zona_service,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
            zona_id=zona.zona_id,
            canal_selectividad_id=(
                canal.canal_selectividad_id
            ),
            zona_nombre=zona.nombre,
            canal_nombre=canal.nombre,
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

    @staticmethod
    def _find_tariff(
        zona: Zona,
        canal: CanalSelectividad,
    ) -> TarifaZonaCanalSelectividad | None:
        for tarifa in zona.tarifas_por_canal:
            if (
                tarifa.canal_selectividad_id
                == canal.canal_selectividad_id
            ):
                return tarifa

        return None

    @staticmethod
    def _format_amount(
        amount: Decimal,
    ) -> str:
        return f"{amount:,.2f}".replace(
            ",",
            "_",
        ).replace(
            ".",
            ",",
        ).replace(
            "_",
            ".",
        )

    def _open_truck_additions(self) -> None:
        window = AdicionalesCamionesWindow(
            parent=self,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
        )

        self.wait_window(window)
        self._refresh_all()

    def _open_day_hour_additions(self) -> None:
        window = AdicionalesDiaHoraWindow(
            parent=self,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
            ),
        )

        self.wait_window(window)
        self._refresh_all()

    def _open_summary(self) -> None:
        window = ResumenEsquemaWindow(
            parent=self,
            esquema_cotizacion_id=(
                self.esquema_cotizacion_id
        ),
    )

        self.wait_window(window)