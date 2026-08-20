import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from validacion_honorarios.db.models import (
    DiaHora,
    TarifaAdicionalDiaHora,
)
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
    TarifaDiaHoraService,
)
from validacion_honorarios.ui.monto_dia_hora_dialog import (
    MontoDiaHoraDialog,
)


class AdicionalesDiaHoraWindow(tk.Toplevel):
    """Matriz semanal de adicionales por día y hora."""

    DIAS = {
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado",
        7: "Domingo",
    }

    def __init__(
        self,
        parent: tk.Misc,
        esquema_cotizacion_id: int,
    ) -> None:
        super().__init__(parent)

        self.esquema_cotizacion_id = esquema_cotizacion_id
        self.esquema_service = EsquemaCotizacionService()
        self.tarifa_service = TarifaDiaHoraService()
        self.esquema = self.esquema_service.obtener(
            esquema_cotizacion_id
        )

        self.tarifas: list[TarifaAdicionalDiaHora] = []
        self.catalogo: list[DiaHora] = []
        self.posicion_por_clave: dict[tuple[int, int], DiaHora] = {}
        self.tarifa_por_posicion_id: dict[int, TarifaAdicionalDiaHora] = {}
        self.selected_ids: set[int] = set()

        self.selection_var = tk.StringVar(
            value="Ninguna posición seleccionada."
        )
        self.status_var = tk.StringVar(value="")
        self.hora_desde_var = tk.StringVar(value="00")
        self.hora_hasta_var = tk.StringVar(value="23")

        self._configure_window()
        self._build_interface()
        self._refresh_all()

        self.transient(parent)

    def _configure_window(self) -> None:
        self.title("Adicionales por día y hora")
        self.geometry("1500x820")
        self.minsize(1050, 650)

    def _build_interface(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_matrix()
        self._build_footer()

    def _build_header(self) -> None:
        proveedor = self.esquema.proveedor

        header = ttk.Frame(self, padding=(14, 14, 14, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Adicionales por día y hora",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(
            header,
            text=(
                f"Esquema {self.esquema.esquema_cotizacion_id}"
                f" | {proveedor.razon_social}"
                f" | {self.esquema.moneda_codigo}"
            ),
        ).grid(row=1, column=0, sticky=tk.W, pady=(6, 0))

        ttk.Label(
            header,
            textvariable=self.status_var,
        ).grid(row=0, column=1, rowspan=2, sticky=tk.E, padx=(20, 0))

    def _build_controls(self) -> None:
        controls = ttk.LabelFrame(
            self,
            text="Configuración y selección",
            padding=10,
        )
        controls.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 10),
        )

        ttk.Button(
            controls,
            text="Inicializar 168 posiciones",
            command=self._initialize_configuration,
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            controls,
            text="Eliminar configuración",
            command=self._delete_configuration,
        ).grid(row=0, column=1, sticky="w", padx=(8, 18))

        ttk.Separator(
            controls,
            orient=tk.VERTICAL,
        ).grid(row=0, column=2, rowspan=2, sticky="ns", padx=(0, 18))

        ttk.Label(
            controls,
            text="Días",
        ).grid(row=0, column=3, sticky="w")

        self.days_list = tk.Listbox(
            controls,
            selectmode=tk.EXTENDED,
            exportselection=False,
            height=3,
            width=18,
        )
        self.days_list.grid(
            row=1,
            column=3,
            rowspan=2,
            sticky="nsew",
            pady=(4, 0),
        )

        for day_number in range(1, 8):
            self.days_list.insert(
                tk.END,
                self.DIAS[day_number],
            )

        ttk.Label(
            controls,
            text="Desde",
        ).grid(row=0, column=4, sticky="w", padx=(12, 0))

        ttk.Label(
            controls,
            text="Hasta",
        ).grid(row=0, column=5, sticky="w", padx=(8, 0))

        hour_values = tuple(f"{hour:02d}" for hour in range(24))

        ttk.Combobox(
            controls,
            textvariable=self.hora_desde_var,
            state="readonly",
            values=hour_values,
            width=6,
        ).grid(row=1, column=4, sticky="w", padx=(12, 0), pady=(4, 0))

        ttk.Combobox(
            controls,
            textvariable=self.hora_hasta_var,
            state="readonly",
            values=hour_values,
            width=6,
        ).grid(row=1, column=5, sticky="w", padx=(8, 0), pady=(4, 0))

        ttk.Button(
            controls,
            text="Seleccionar rango",
            command=self._select_range,
        ).grid(row=1, column=6, sticky="w", padx=(12, 0), pady=(4, 0))

        ttk.Button(
            controls,
            text="Semana completa",
            command=self._select_all,
        ).grid(row=1, column=7, sticky="w", padx=(8, 0), pady=(4, 0))

        ttk.Button(
            controls,
            text="Limpiar selección",
            command=self._clear_selection,
        ).grid(row=1, column=8, sticky="w", padx=(8, 0), pady=(4, 0))

        controls.columnconfigure(3, weight=1)

    def _build_matrix(self) -> None:
        matrix_frame = ttk.Frame(self, padding=(14, 0, 14, 0))
        matrix_frame.grid(row=2, column=0, sticky="nsew")
        matrix_frame.columnconfigure(0, weight=1)
        matrix_frame.rowconfigure(1, weight=1)

        ttk.Label(
            matrix_frame,
            text=(
                "Haz clic en una celda para alternar su selección. "
                "Las acciones inferiores se aplican a todas las posiciones seleccionadas."
            ),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        table_frame = ttk.Frame(matrix_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = [
            "dia",
            *[f"hora_{hour:02d}" for hour in range(24)],
        ]

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="none",
            height=7,
        )
        self.table.grid(row=0, column=0, sticky="nsew")

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview,
        )
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.table.xview,
        )
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.table.heading("dia", text="Día")
        self.table.column(
            "dia",
            width=110,
            minwidth=95,
            anchor=tk.W,
            stretch=False,
        )

        for hour in range(24):
            column_name = f"hora_{hour:02d}"
            self.table.heading(column_name, text=f"{hour:02d}:00")
            self.table.column(
                column_name,
                width=82,
                minwidth=72,
                anchor=tk.E,
                stretch=False,
            )

        self.table.bind("<Button-1>", self._table_click)

        actions = ttk.Frame(matrix_frame)
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        actions.columnconfigure(3, weight=1)

        ttk.Button(
            actions,
            text="Asignar importe a selección",
            command=self._assign_amount,
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            actions,
            text="Restablecer selección a cero",
            command=self._reset_selection,
        ).grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Button(
            actions,
            text="Actualizar matriz",
            command=self._refresh_all,
        ).grid(row=0, column=2, sticky="w", padx=(8, 0))

        ttk.Label(
            actions,
            textvariable=self.selection_var,
        ).grid(row=0, column=3, sticky="e", padx=(16, 0))

    def _build_footer(self) -> None:
        footer = ttk.Frame(self, padding=14)
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)

        ttk.Label(
            footer,
            text=(
                "Una configuración activa contiene 168 posiciones. "
                "El importe cero indica que no hay adicional en esa hora."
            ),
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            footer,
            text="Cerrar",
            command=self.destroy,
        ).grid(row=0, column=1, sticky="e")

    def _refresh_all(self) -> None:
        try:
            self.catalogo = self.tarifa_service.listar_catalogo()
            self.tarifas = self.tarifa_service.listar(
                self.esquema_cotizacion_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudieron cargar los datos",
                message=str(exc),
                parent=self,
            )
            return

        self.posicion_por_clave = {
            (position.dia, position.hora): position
            for position in self.catalogo
        }
        self.tarifa_por_posicion_id = {
            tariff.dia_hora_id: tariff
            for tariff in self.tarifas
        }

        valid_ids = set(self.tarifa_por_posicion_id)
        self.selected_ids.intersection_update(valid_ids)

        self._refresh_matrix()
        self._refresh_selection_description()
        self._refresh_status()

    def _refresh_matrix(self) -> None:
        children = self.table.get_children()
        if children:
            self.table.delete(*children)

        for day_number in range(1, 8):
            values = [self.DIAS[day_number]]

            for hour in range(24):
                position = self.posicion_por_clave.get(
                    (day_number, hour)
                )

                if position is None:
                    values.append("-")
                    continue

                tariff = self.tarifa_por_posicion_id.get(
                    position.dia_hora_id
                )

                if tariff is None:
                    values.append("")
                    continue

                formatted = self._format_amount(tariff.monto)

                if position.dia_hora_id in self.selected_ids:
                    formatted = f"[{formatted}]"

                values.append(formatted)

            self.table.insert(
                "",
                tk.END,
                iid=f"dia_{day_number}",
                values=values,
            )

    def _table_click(self, event: tk.Event) -> None:
        if self.table.identify_region(event.x, event.y) != "cell":
            return

        row_id = self.table.identify_row(event.y)
        column_id = self.table.identify_column(event.x)

        if not row_id:
            return

        try:
            day_number = int(row_id.removeprefix("dia_"))
            column_number = int(column_id.removeprefix("#"))
        except ValueError:
            return

        if column_number <= 1:
            return

        hour = column_number - 2
        position = self.posicion_por_clave.get(
            (day_number, hour)
        )

        if position is None:
            return

        position_id = position.dia_hora_id

        if position_id not in self.tarifa_por_posicion_id:
            messagebox.showinfo(
                title="Configuración no inicializada",
                message=(
                    "Inicializa las 168 posiciones antes de seleccionar horas."
                ),
                parent=self,
            )
            return

        if position_id in self.selected_ids:
            self.selected_ids.remove(position_id)
        else:
            self.selected_ids.add(position_id)

        self._refresh_matrix()
        self._refresh_selection_description()

    def _select_range(self) -> None:
        selected_days = self.days_list.curselection()

        if not selected_days:
            messagebox.showinfo(
                title="Seleccionar días",
                message="Selecciona al menos un día.",
                parent=self,
            )
            return

        try:
            hour_from = int(self.hora_desde_var.get())
            hour_to = int(self.hora_hasta_var.get())
        except ValueError:
            return

        if hour_to < hour_from:
            messagebox.showwarning(
                title="Rango horario inválido",
                message="La hora hasta no puede ser menor que la hora desde.",
                parent=self,
            )
            return

        if len(self.tarifas) != TarifaDiaHoraService.CANTIDAD_POSICIONES:
            messagebox.showinfo(
                title="Configuración no inicializada",
                message=(
                    "Inicializa las 168 posiciones antes de seleccionar rangos."
                ),
                parent=self,
            )
            return

        for list_index in selected_days:
            day_number = list_index + 1

            for hour in range(hour_from, hour_to + 1):
                position = self.posicion_por_clave.get(
                    (day_number, hour)
                )

                if position is not None:
                    self.selected_ids.add(position.dia_hora_id)

        self._refresh_matrix()
        self._refresh_selection_description()

    def _select_all(self) -> None:
        if len(self.tarifas) != TarifaDiaHoraService.CANTIDAD_POSICIONES:
            messagebox.showinfo(
                title="Configuración no inicializada",
                message=(
                    "Inicializa las 168 posiciones antes de seleccionar la semana."
                ),
                parent=self,
            )
            return

        self.selected_ids = set(self.tarifa_por_posicion_id)
        self._refresh_matrix()
        self._refresh_selection_description()

    def _clear_selection(self) -> None:
        self.selected_ids.clear()
        self._refresh_matrix()
        self._refresh_selection_description()

    def _initialize_configuration(self) -> None:
        if len(self.tarifas) == TarifaDiaHoraService.CANTIDAD_POSICIONES:
            messagebox.showinfo(
                title="Configuración existente",
                message="La configuración horaria ya está inicializada.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            title="Inicializar configuración horaria",
            message=(
                "Se crearán 168 posiciones con importe cero. "
                "¿Deseas continuar?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.tarifa_service.inicializar(
                self.esquema_cotizacion_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo inicializar",
                message=str(exc),
                parent=self,
            )
            return

        self._refresh_all()

    def _delete_configuration(self) -> None:
        if not self.tarifas:
            messagebox.showinfo(
                title="Sin configuración",
                message="El esquema no tiene una configuración horaria.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            title="Eliminar configuración horaria",
            message=(
                "Se eliminarán las 168 posiciones y todos sus importes. "
                "¿Deseas continuar?"
            ),
            parent=self,
        )

        if not confirmed:
            return

        try:
            self.tarifa_service.eliminar_configuracion(
                self.esquema_cotizacion_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo eliminar",
                message=str(exc),
                parent=self,
            )
            return

        self.selected_ids.clear()
        self._refresh_all()

    def _assign_amount(self) -> None:
        if not self.selected_ids:
            messagebox.showinfo(
                title="Seleccionar posiciones",
                message="Selecciona al menos una posición horaria.",
                parent=self,
            )
            return

        dialog = MontoDiaHoraDialog(
            parent=self,
            service=self.tarifa_service,
            esquema_cotizacion_id=self.esquema_cotizacion_id,
            dia_hora_ids=sorted(self.selected_ids),
            descripcion_seleccion=self._selection_summary(),
            moneda_codigo=self.esquema.moneda_codigo,
        )

        self.wait_window(dialog)

        if dialog.resultado_guardado:
            self._refresh_all()

    def _reset_selection(self) -> None:
        if not self.selected_ids:
            messagebox.showinfo(
                title="Seleccionar posiciones",
                message="Selecciona al menos una posición horaria.",
                parent=self,
            )
            return

        try:
            self.tarifa_service.restablecer_montos(
                esquema_cotizacion_id=self.esquema_cotizacion_id,
                dia_hora_ids=sorted(self.selected_ids),
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo restablecer",
                message=str(exc),
                parent=self,
            )
            return

        self._refresh_all()

    def _refresh_selection_description(self) -> None:
        self.selection_var.set(self._selection_summary())

    def _selection_summary(self) -> str:
        count = len(self.selected_ids)

        if count == 0:
            return "Ninguna posición seleccionada."

        selected_positions = [
            position
            for position in self.catalogo
            if position.dia_hora_id in self.selected_ids
        ]

        if count == 1 and selected_positions:
            return (
                "1 posición seleccionada: "
                f"{selected_positions[0].descripcion}."
            )

        return f"{count} posiciones seleccionadas."

    def _refresh_status(self) -> None:
        count = len(self.tarifas)
        positive_count = sum(
            1
            for tariff in self.tarifas
            if tariff.monto > Decimal("0.00")
        )

        if count == 0:
            text = "Configuración horaria no inicializada."
        elif count == TarifaDiaHoraService.CANTIDAD_POSICIONES:
            text = (
                "168 posiciones configuradas | "
                f"{positive_count} con adicional | "
                f"{168 - positive_count} en cero"
            )
        else:
            text = f"Configuración incompleta: {count} de 168 posiciones."

        self.status_var.set(text)

    @staticmethod
    def _format_amount(amount: Decimal) -> str:
        return (
            f"{amount:,.2f}"
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )
