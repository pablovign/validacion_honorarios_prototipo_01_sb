import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from validacion_honorarios.services import (
    ApplicationError,
    ResumenEsquemaService,
)


class ResumenEsquemaWindow(tk.Toplevel):
    """Vista integral y de solo lectura de un esquema."""

    def __init__(
        self,
        parent: tk.Misc,
        esquema_cotizacion_id: int,
    ) -> None:
        super().__init__(parent)

        self.esquema_cotizacion_id = esquema_cotizacion_id
        self.service = ResumenEsquemaService()
        self.resumen: dict = {}

        self._configure_window()
        self._build_interface()
        self._load_data()

        self.transient(parent)

    def _configure_window(self) -> None:
        self.title("Vista general del esquema")
        self.geometry("1350x820")
        self.minsize(1000, 650)

    def _build_interface(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=14)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(
            header,
            text="Vista general del esquema",
            style="SectionTitle.TLabel",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.state_label = ttk.Label(
            header,
            text="",
        )
        self.state_label.grid(row=0, column=1, sticky="e")

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=14,
            pady=(0, 10),
        )

        self.general_tab = ttk.Frame(self.notebook, padding=16)
        self.main_tariffs_tab = ttk.Frame(self.notebook, padding=16)
        self.trucks_tab = ttk.Frame(self.notebook, padding=16)
        self.schedule_tab = ttk.Frame(self.notebook, padding=16)
        self.validation_tab = ttk.Frame(self.notebook, padding=16)

        self.notebook.add(self.general_tab, text="Datos generales")
        self.notebook.add(
            self.main_tariffs_tab,
            text="Tarifas principales",
        )
        self.notebook.add(self.trucks_tab, text="Camiones")
        self.notebook.add(self.schedule_tab, text="Día y hora")
        self.notebook.add(
            self.validation_tab,
            text="Comprobación",
        )

        footer = ttk.Frame(self, padding=(14, 0, 14, 14))
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)

        ttk.Label(
            footer,
            text=(
                "Vista de solo lectura. Los datos se obtienen "
                "directamente del esquema almacenado."
            ),
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            footer,
            text="Actualizar resumen",
            command=self._load_data,
        ).grid(row=0, column=1, padx=(8, 0))

        ttk.Button(
            footer,
            text="Cerrar",
            command=self.destroy,
        ).grid(row=0, column=2, padx=(8, 0))

    def _load_data(self) -> None:
        try:
            self.resumen = self.service.obtener(
                self.esquema_cotizacion_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo cargar el resumen",
                message=str(exc),
                parent=self,
            )
            return
        except Exception as exc:
            messagebox.showerror(
                title="Error inesperado",
                message=(
                    "No se pudo construir la vista general.\n\n"
                    f"Detalle técnico:\n{exc}"
                ),
                parent=self,
            )
            return

        general = self.resumen["general"]
        self.title_label.configure(
            text=(
                "Vista general del esquema "
                f"{general['esquema_cotizacion_id']}"
            )
        )
        self.state_label.configure(
            text=f"Estado: {general['estado']}"
        )

        self._build_general_tab()
        self._build_main_tariffs_tab()
        self._build_trucks_tab()
        self._build_schedule_tab()
        self._build_validation_tab()

    @staticmethod
    def _clear_frame(frame: ttk.Frame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _build_general_tab(self) -> None:
        self._clear_frame(self.general_tab)
        general = self.resumen["general"]

        data_frame = ttk.LabelFrame(
            self.general_tab,
            text="Identificación",
            padding=14,
        )
        data_frame.pack(fill=tk.X, pady=(0, 14))
        data_frame.columnconfigure(1, weight=1)
        data_frame.columnconfigure(3, weight=1)

        values = (
            ("Proveedor", general["proveedor"]),
            ("CUIT", general["cuit"]),
            (
                "Aduana",
                f"{general['aduana_codigo']} - "
                f"{general['aduana_nombre']}",
            ),
            (
                "Fecha de inicio",
                general["fecha_inicio"].strftime("%d/%m/%Y"),
            ),
            (
                "Fecha de finalización",
                (
                    general["fecha_fin"].strftime("%d/%m/%Y")
                    if general["fecha_fin"]
                    else "Sin definir"
                ),
            ),
            ("Moneda", general["moneda_codigo"]),
        )

        for index, (label, value) in enumerate(values):
            row = index // 2
            pair_column = (index % 2) * 2

            ttk.Label(
                data_frame,
                text=f"{label}:",
            ).grid(
                row=row,
                column=pair_column,
                sticky="nw",
                padx=(0, 8),
                pady=5,
            )
            ttk.Label(
                data_frame,
                text=str(value),
                wraplength=430,
            ).grid(
                row=row,
                column=pair_column + 1,
                sticky="nw",
                padx=(0, 24),
                pady=5,
            )

        notes_frame = ttk.LabelFrame(
            self.general_tab,
            text="Observaciones",
            padding=14,
        )
        notes_frame.pack(fill=tk.BOTH, expand=True)

        observations = general["observaciones"] or "Sin observaciones."
        text = tk.Text(
            notes_frame,
            wrap=tk.WORD,
            height=12,
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.insert("1.0", observations)
        text.configure(state=tk.DISABLED)

    def _build_main_tariffs_tab(self) -> None:
        self._clear_frame(self.main_tariffs_tab)

        channels = self.resumen["canales"]
        rows = self.resumen["tarifas_principales"]

        if not rows:
            ttk.Label(
                self.main_tariffs_tab,
                text="El esquema no tiene zonas cargadas.",
            ).pack(anchor=tk.W)
            return

        columns = [
            "zona",
            *[
                f"canal_{channel['canal_selectividad_id']}"
                for channel in channels
            ],
        ]

        table_frame = ttk.Frame(self.main_tariffs_tab)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )
        table.grid(row=0, column=0, sticky="nsew")

        vertical = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=table.yview,
        )
        vertical.grid(row=0, column=1, sticky="ns")

        horizontal = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=table.xview,
        )
        horizontal.grid(row=1, column=0, sticky="ew")

        table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )

        table.heading("zona", text="Zona")
        table.column("zona", width=220, anchor=tk.W)

        for channel in channels:
            column = f"canal_{channel['canal_selectividad_id']}"
            table.heading(column, text=channel["nombre"])
            table.column(column, width=150, anchor=tk.E)

        for row in rows:
            values = [row["zona"]]

            for channel in channels:
                amount = row["tarifas"].get(
                    channel["canal_selectividad_id"]
                )
                values.append(
                    self._format_amount(amount)
                    if amount is not None
                    else "Sin cargar"
                )

            table.insert("", tk.END, values=values)

    def _build_trucks_tab(self) -> None:
        self._clear_frame(self.trucks_tab)

        zones = self.resumen["zonas"]
        ranges = self.resumen["tramos_camiones"]

        if not ranges:
            ttk.Label(
                self.trucks_tab,
                text=(
                    "No hay tramos adicionales por camiones "
                    "configurados."
                ),
            ).pack(anchor=tk.W)
            return

        columns = [
            "tramo",
            *[f"zona_{zone['zona_id']}" for zone in zones],
        ]

        table_frame = ttk.Frame(self.trucks_tab)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )
        table.grid(row=0, column=0, sticky="nsew")

        vertical = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=table.yview,
        )
        vertical.grid(row=0, column=1, sticky="ns")

        horizontal = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=table.xview,
        )
        horizontal.grid(row=1, column=0, sticky="ew")

        table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )

        table.heading("tramo", text="Tramo")
        table.column("tramo", width=220, anchor=tk.W)

        for zone in zones:
            column = f"zona_{zone['zona_id']}"
            table.heading(column, text=zone["nombre"])
            table.column(column, width=160, anchor=tk.E)

        for item in ranges:
            values = [item["descripcion"]]

            for zone in zones:
                amount = item["tarifas"].get(zone["zona_id"])
                values.append(
                    self._format_amount(amount)
                    if amount is not None
                    else "Sin cargar"
                )

            table.insert("", tk.END, values=values)

    def _build_schedule_tab(self) -> None:
        self._clear_frame(self.schedule_tab)
        schedule = self.resumen["horario"]

        summary = ttk.LabelFrame(
            self.schedule_tab,
            text="Resumen horario",
            padding=12,
        )
        summary.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            summary,
            text=(
                f"Posiciones: {schedule['cantidad_registros']} | "
                f"Con importe mayor que cero: "
                f"{schedule['cantidad_mayor_cero']} | "
                f"En cero: {schedule['cantidad_en_cero']}"
            ),
        ).pack(anchor=tk.W)

        blocks = schedule["bloques"]

        if not blocks:
            ttk.Label(
                self.schedule_tab,
                text=(
                    "No hay bloques horarios con importe "
                    "mayor que cero."
                ),
            ).pack(anchor=tk.W)
            return

        columns = (
            "dia",
            "desde",
            "hasta",
            "monto",
        )

        table_frame = ttk.Frame(self.schedule_tab)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )
        table.grid(row=0, column=0, sticky="nsew")

        vertical = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=table.yview,
        )
        vertical.grid(row=0, column=1, sticky="ns")
        table.configure(yscrollcommand=vertical.set)

        headings = {
            "dia": "Día",
            "desde": "Desde",
            "hasta": "Hasta",
            "monto": "Importe",
        }

        for column, heading in headings.items():
            table.heading(column, text=heading)

        table.column("dia", width=180, anchor=tk.W)
        table.column("desde", width=120, anchor=tk.CENTER)
        table.column("hasta", width=120, anchor=tk.CENTER)
        table.column("monto", width=180, anchor=tk.E)

        for block in blocks:
            table.insert(
                "",
                tk.END,
                values=(
                    block["nombre_dia"],
                    f"{block['hora_desde']:02d}:00",
                    self._format_end_hour(block["hora_hasta"]),
                    self._format_amount(block["monto"]),
                ),
            )

    def _build_validation_tab(self) -> None:
        self._clear_frame(self.validation_tab)

        columns = (
            "nivel",
            "mensaje",
        )

        table_frame = ttk.Frame(self.validation_tab)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )
        table.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=table.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        table.configure(yscrollcommand=scrollbar.set)

        table.heading("nivel", text="Nivel")
        table.heading("mensaje", text="Detalle")
        table.column("nivel", width=130, anchor=tk.CENTER)
        table.column("mensaje", width=900, anchor=tk.W)

        for warning in self.resumen["advertencias"]:
            table.insert(
                "",
                tk.END,
                values=(
                    warning["nivel"],
                    warning["mensaje"],
                ),
            )

    @staticmethod
    def _format_amount(amount: Decimal) -> str:
        return (
            f"{amount:,.2f}"
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )

    @staticmethod
    def _format_end_hour(hour: int) -> str:
        if hour == 24:
            return "24:00"

        return f"{hour:02d}:00"
