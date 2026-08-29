import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk
import customtkinter as ctk

from validacion_honorarios.db.models import (
    AdicionalCamiones,
    CanalSelectividad,
    TarifaAdicionalCamionesZona,
    TarifaZonaCanalSelectividad,
    Zona,
)
from validacion_honorarios.services import (
    AdicionalCamionesService,
    ApplicationError,
    EsquemaCotizacionService,
    ResumenEsquemaService,
    TarifaDiaHoraService,
    ZonaTarifaService,
)
from validacion_honorarios.ui.monto_camiones_zona_dialog import (
    MontoCamionesZonaDialog,
)
from validacion_honorarios.ui.monto_dia_hora_dialog import (
    MontoDiaHoraDialog,
)
from validacion_honorarios.ui.monto_tarifa_dialog import (
    MontoTarifaDialog,
)
from validacion_honorarios.ui.tramo_camiones_dialog import (
    TramoCamionesDialog,
)
from validacion_honorarios.ui.zona_dialog import ZonaDialog
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
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    FONT_FAMILY,
    apply_global_ttk_theme,
    apply_treeview_row_tags,
    style_treeview,
)



class EsquemaWizardWindow(ctk.CTkToplevel):
    """Wizard moderno para crear o continuar un esquema de cotización."""

    STEP_NAMES = (
        "1. Datos generales",
        "2. Zonas y tarifas",
        "3. Camiones",
        "4. Día y hora",
        "5. Revisión",
    )

    def __init__(
        self,
        parent: tk.Misc,
        esquema_cotizacion_id: int | None = None,
    ) -> None:
        super().__init__(parent)

        self.esquema_service = EsquemaCotizacionService()
        self.zona_service = ZonaTarifaService()
        self.camiones_service = AdicionalCamionesService()
        self.horario_service = TarifaDiaHoraService()
        self.resumen_service = ResumenEsquemaService()

        self.esquema_cotizacion_id = esquema_cotizacion_id
        self.esquema = None
        self.current_step = 0 if esquema_cotizacion_id is None else 4
        self.resultado_guardado = False

        self.steps: list[ttk.Frame] = []
        self.step_buttons: list[ctk.CTkButton] = []

        self._configure_window()
        self._build_shell()
        self._build_steps()
        self._load_scheme()
        self._show_step(self.current_step)

        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._close)

    @property
    def editable(self) -> bool:
        return self.esquema is None or self.esquema.estado == "BORRADOR"

    def _configure_window(self) -> None:
        apply_global_ttk_theme()
        self.title("Asistente de Esquema de Cotización")
        self.geometry("1450x860")
        self.minsize(1080, 680)

    def _build_shell(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header Superior
        header = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=0,
            border_width=0,
        )
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill=tk.X, padx=24, pady=16)

        title_lbl = ctk.CTkLabel(
            header_inner,
            text="⚡ Asistente de Esquema de Cotización",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w")

        self.header_status = ctk.CTkLabel(
            header_inner,
            text="Nuevo esquema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.header_status.pack(anchor="w", pady=(2, 0))

        # Barra de Navegación de Pasos (Stepper)
        nav_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        nav_card.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 14))

        nav = ctk.CTkFrame(nav_card, fg_color="transparent")
        nav.pack(fill=tk.X, padx=20, pady=10)

        for index, name in enumerate(self.STEP_NAMES):
            button = ctk.CTkButton(
                nav,
                text=name,
                font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                fg_color="transparent",
                text_color=COLOR_TEXT_MUTED,
                hover_color=COLOR_BG_CARD,
                height=36,
                corner_radius=8,
                command=lambda value=index: self._request_step(value),
            )
            button.grid(row=0, column=index, sticky="ew", padx=4)
            nav.columnconfigure(index, weight=1)
            self.step_buttons.append(button)

        # Contenedor de Pasos
        self.content = ttk.Frame(self, padding=(20, 0, 20, 8))
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        # Footer
        footer_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        footer_card.grid(row=3, column=0, sticky="ew")

        footer = ctk.CTkFrame(footer_card, fg_color="transparent")
        footer.pack(fill=tk.X, padx=24, pady=14)

        self.back_button = ctk.CTkButton(
            footer,
            text="← Atrás",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._back,
        )
        self.back_button.pack(side="left")

        self.next_button = ctk.CTkButton(
            footer,
            text="Guardar y continuar →",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._next,
        )
        self.next_button.pack(side="left", padx=(8, 0))

        self.footer_message = ctk.CTkLabel(
            footer,
            text="* Los cambios de matrices se guardan al confirmar cada operación.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        self.footer_message.pack(side="left", padx=(18, 0))

        self.close_button = ctk.CTkButton(
            footer,
            text="Guardar borrador y cerrar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._close,
        )
        self.close_button.pack(side="right")

        self.approve_button = ctk.CTkButton(
            footer,
            text="✓ Aprobar esquema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            corner_radius=8,
            height=36,
            command=self._approve,
        )
        self.approve_button.pack(side="right", padx=(0, 8))


    def _build_steps(self) -> None:
        self.general_step = GeneralStep(
            self.content,
            wizard=self,
        )
        self.zones_step = ZonesTariffsStep(
            self.content,
            wizard=self,
        )
        self.trucks_step = TrucksStep(
            self.content,
            wizard=self,
        )
        self.schedule_step = ScheduleStep(
            self.content,
            wizard=self,
        )
        self.review_step = ReviewStep(
            self.content,
            wizard=self,
        )

        self.steps = [
            self.general_step,
            self.zones_step,
            self.trucks_step,
            self.schedule_step,
            self.review_step,
        ]

        for frame in self.steps:
            frame.grid(row=0, column=0, sticky="nsew")

    def _load_scheme(self) -> None:
        if self.esquema_cotizacion_id is None:
            self.esquema = None
            self.header_status.configure(text="Nuevo esquema, todavía no guardado")
            self._update_navigation()
            return

        try:
            self.esquema = self.esquema_service.obtener(
                self.esquema_cotizacion_id
            )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo cargar el esquema",
                message=str(exc),
                parent=self,
            )
            self.destroy()
            return

        proveedor = self.esquema.proveedor
        self.header_status.configure(
            text=(
                f"Esquema {self.esquema.esquema_cotizacion_id} | "
                f"{proveedor.razon_social} | "
                f"{self.esquema.estado} | {self.esquema.moneda_codigo}"
            )
        )
        self._update_navigation()

    def refresh_scheme(self) -> None:
        self._load_scheme()
        self.steps[self.current_step].refresh()

    def _request_step(self, index: int) -> None:
        if self.esquema_cotizacion_id is None and index > 0:
            messagebox.showinfo(
                title="Guardar datos generales",
                message=(
                    "Guarda primero los datos generales para crear el borrador "
                    "y su zona GENERAL."
                ),
                parent=self,
            )
            return
        self._show_step(index)

    def _show_step(self, index: int) -> None:
        if self.esquema_cotizacion_id is None and index > 0:
            index = 0

        self.current_step = max(0, min(index, len(self.steps) - 1))
        frame = self.steps[self.current_step]
        frame.tkraise()
        frame.refresh()
        self._update_navigation()

    def _update_navigation(self) -> None:
        for index, button in enumerate(self.step_buttons):
            if self.esquema is not None and self.esquema.estado != "BORRADOR":
                allowed = index == len(self.steps) - 1
            else:
                allowed = self.esquema_cotizacion_id is not None or index == 0

            button.configure(state=tk.NORMAL if allowed else tk.DISABLED)

            if index == self.current_step:
                button.configure(
                    fg_color=COLOR_PRIMARY[0],
                    text_color="#FFFFFF",
                )
            elif allowed:
                button.configure(
                    fg_color="transparent",
                    text_color=COLOR_TEXT_PRIMARY[0],
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=COLOR_TEXT_MUTED[0],
                )

        back_enabled = (
            self.current_step > 0
            and (self.esquema is None or self.esquema.estado == "BORRADOR")
        )
        self.back_button.configure(
            state=tk.NORMAL if back_enabled else tk.DISABLED
        )

        if self.current_step == 0:
            self.next_button.pack(side="left", padx=(8, 0))
            self.next_button.configure(
                text="Guardar y continuar →" if self.editable else "Siguiente →"
            )
        elif self.current_step == len(self.steps) - 1:
            self.next_button.pack_forget()
        else:
            self.next_button.pack(side="left", padx=(8, 0))
            self.next_button.configure(text="Siguiente →")

        approve_visible = (
            self.current_step == len(self.steps) - 1
            and self.esquema is not None
            and self.esquema.estado == "BORRADOR"
        )
        if approve_visible:
            self.approve_button.pack(side="right", padx=(0, 8))
        else:
            self.approve_button.pack_forget()

        self.close_button.configure(
            text=(
                "Guardar borrador y cerrar"
                if self.esquema is None or self.esquema.estado == "BORRADOR"
                else "Cerrar"
            )
        )


    def _back(self) -> None:
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _next(self) -> None:
        if self.current_step == 0 and self.editable:
            if not self.general_step.save():
                return

        if self.current_step < len(self.steps) - 1:
            self._show_step(self.current_step + 1)
        else:
            self._close()

    def _approve(self) -> None:
        if self.esquema_cotizacion_id is None:
            return
        confirmed = messagebox.askyesno(
            title="Aprobar esquema",
            message=(
                "Al aprobar, el esquema dejará de ser editable.\n\n"
                "Las combinaciones sin tarifa continuarán como "
                "advertencias informativas.\n\n"
                "¿Deseas continuar?"
            ),
            parent=self,
        )
        if not confirmed:
            return
        try:
            self.esquema_service.aprobar(self.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo aprobar",
                message=str(exc),
                parent=self,
            )
            self.review_step.refresh()
            return
        self.resultado_guardado = True
        self._load_scheme()
        self.review_step.refresh()
        self._update_navigation()
        messagebox.showinfo(
            title="Esquema aprobado",
            message=(
                "El esquema fue aprobado y quedó disponible "
                "en modo de solo lectura."
            ),
            parent=self,
        )

    def _close(self) -> None:
        if self.esquema_cotizacion_id is None:
            confirmed = messagebox.askyesno(
                title="Cerrar sin guardar",
                message=(
                    "El esquema todavía no fue creado. "
                    "¿Deseas cerrar sin guardar?"
                ),
                parent=self,
            )
            if not confirmed:
                return
        self.destroy()


class WizardStep(ttk.Frame):
    def __init__(self, parent: tk.Misc, wizard: EsquemaWizardWindow) -> None:
        super().__init__(parent)
        self.wizard = wizard

    def refresh(self) -> None:
        pass

    @staticmethod
    def format_amount(value: Decimal) -> str:
        return (
            f"{value:,.2f}"
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )


class GeneralStep(WizardStep):
    def __init__(self, parent: tk.Misc, wizard: EsquemaWizardWindow) -> None:
        super().__init__(parent, wizard)

        self.provider_var = tk.StringVar()
        self.customs_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.currency_var = tk.StringVar(value="ARS")
        self.providers_by_label = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(
            self,
            text="1. Datos generales",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Label(
            self,
            text=(
                "Guarda la cabecera para crear el esquema en BORRADOR y "
                "la zona inicial GENERAL."
            ),
        ).grid(row=1, column=0, sticky="w", pady=(0, 14))

        form = ttk.LabelFrame(self, text="Cabecera", padding=18)
        form.grid(row=2, column=0, sticky="nsew")
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.rowconfigure(7, weight=1)

        ttk.Label(form, text="Proveedor").grid(row=0, column=0, columnspan=2, sticky="w")
        self.provider_combo = ttk.Combobox(
            form,
            textvariable=self.provider_var,
            state="readonly",
        )
        self.provider_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 12))
        self.provider_combo.bind("<<ComboboxSelected>>", self._provider_changed)

        ttk.Label(form, text="Aduana asociada").grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Entry(
            form,
            textvariable=self.customs_var,
            state="readonly",
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        ttk.Label(form, text="Fecha de inicio").grid(row=4, column=0, sticky="w")
        ttk.Label(form, text="Moneda").grid(row=4, column=1, sticky="w", padx=(12, 0))

        ttk.Entry(
            form,
            textvariable=self.start_date_var,
        ).grid(row=5, column=0, sticky="ew", pady=(4, 12))

        ttk.Combobox(
            form,
            textvariable=self.currency_var,
            state="readonly",
            values=("ARS", "USD"),
        ).grid(row=5, column=1, sticky="ew", padx=(12, 0), pady=(4, 12))

        ttk.Label(form, text="Observaciones").grid(row=6, column=0, columnspan=2, sticky="w")
        self.notes_text = tk.Text(form, height=9, wrap=tk.WORD)
        self.notes_text.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(4, 0))

    def refresh(self) -> None:
        try:
            providers = self.wizard.esquema_service.listar_proveedores()
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudieron cargar los proveedores",
                message=str(exc),
                parent=self.wizard,
            )
            return

        self.providers_by_label = {}
        values = []

        for provider in providers:
            label = f"{provider.razon_social} | CUIT {provider.cuit}"
            values.append(label)
            self.providers_by_label[label] = provider

        self.provider_combo.configure(values=values)

        scheme = self.wizard.esquema
        if scheme is None:
            if values and not self.provider_var.get():
                self.provider_var.set(values[0])
                self._provider_changed()
            if not self.start_date_var.get():
                from datetime import date
                self.start_date_var.set(date.today().strftime("%d/%m/%Y"))
            return

        provider = scheme.proveedor
        label = f"{provider.razon_social} | CUIT {provider.cuit}"
        self.provider_var.set(label)
        self.customs_var.set(
            f"{provider.aduana.codigo} - {provider.aduana.nombre}"
        )
        self.start_date_var.set(scheme.fecha_inicio.strftime("%d/%m/%Y"))
        self.currency_var.set(scheme.moneda_codigo)
        self.notes_text.delete("1.0", tk.END)
        if scheme.observaciones:
            self.notes_text.insert("1.0", scheme.observaciones)

        state = tk.NORMAL if self.wizard.editable else tk.DISABLED
        self.provider_combo.configure(state="readonly" if state == tk.NORMAL else tk.DISABLED)

    def _provider_changed(self, _event=None) -> None:
        provider = self.providers_by_label.get(self.provider_var.get())
        if provider is None:
            self.customs_var.set("")
            return
        self.customs_var.set(
            f"{provider.aduana.codigo} - {provider.aduana.nombre}"
        )

    def save(self) -> bool:
        provider = self.providers_by_label.get(self.provider_var.get())
        if provider is None:
            messagebox.showwarning(
                title="Proveedor obligatorio",
                message="Selecciona un proveedor.",
                parent=self.wizard,
            )
            return False

        notes = self.notes_text.get("1.0", tk.END)

        try:
            if self.wizard.esquema_cotizacion_id is None:
                scheme = self.wizard.esquema_service.crear(
                    proveedor_id=provider.proveedor_id,
                    fecha_inicio=self.start_date_var.get(),
                    moneda_codigo=self.currency_var.get(),
                    observaciones=notes,
                )
                self.wizard.esquema_cotizacion_id = scheme.esquema_cotizacion_id
            else:
                self.wizard.esquema_service.actualizar(
                    esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
                    proveedor_id=provider.proveedor_id,
                    fecha_inicio=self.start_date_var.get(),
                    moneda_codigo=self.currency_var.get(),
                    observaciones=notes,
                )
        except ApplicationError as exc:
            messagebox.showwarning(
                title="No se pudo guardar",
                message=str(exc),
                parent=self.wizard,
            )
            return False

        self.wizard.resultado_guardado = True
        self.wizard._load_scheme()
        return True


class ZonesTariffsStep(WizardStep):
    def __init__(self, parent: tk.Misc, wizard: EsquemaWizardWindow) -> None:
        super().__init__(parent, wizard)

        self.zones: list[Zona] = []
        self.channels: list[CanalSelectividad] = []
        self.zone_by_id = {}
        self.channel_by_column = {}
        self.selected_zone_id = None
        self.selected_channel_id = None
        self.selection_var = tk.StringVar(value="Ninguna tarifa seleccionada.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(
            self,
            text="2. Zonas y tarifas principales",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Label(
            self,
            text=(
                "Mantén GENERAL si no hay división por zonas. "
                "La matriz permite un importe distinto por zona y canal."
            ),
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        body = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        body.grid(row=2, column=0, sticky="nsew")

        left = ttk.Frame(body, padding=10)
        right = ttk.Frame(body, padding=10)
        body.add(left, weight=1)
        body.add(right, weight=4)

        ttk.Label(left, text="Zonas", style="SectionTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.zone_list = tk.Listbox(left, exportselection=False)
        self.zone_list.pack(fill=tk.BOTH, expand=True)
        self.zone_list.bind("<Double-1>", lambda _event: self.edit_zone())

        zone_actions = ttk.Frame(left)
        zone_actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(zone_actions, text="Nueva", command=self.new_zone).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(zone_actions, text="Editar", command=self.edit_zone).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(zone_actions, text="Eliminar", command=self.delete_zone).pack(fill=tk.X)

        ttk.Label(right, text="Matriz Zona × Canal", style="SectionTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        table_frame = ttk.Frame(right)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.table = ttk.Treeview(table_frame, show="headings", selectmode="browse")
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.bind("<Button-1>", self._table_click)
        self.table.bind("<Double-1>", self._table_double_click)

        ybar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        ybar.grid(row=0, column=1, sticky="ns")
        xbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        xbar.grid(row=1, column=0, sticky="ew")
        self.table.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        ttk.Label(right, textvariable=self.selection_var).pack(fill=tk.X, pady=(8, 0))

        actions = ttk.Frame(right)
        actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(actions, text="Editar tarifa", command=self.edit_tariff).pack(side=tk.LEFT)
        ttk.Button(actions, text="Quitar tarifa", command=self.remove_tariff).pack(side=tk.LEFT, padx=(8, 0))

    def refresh(self) -> None:
        if self.wizard.esquema_cotizacion_id is None:
            return
        try:
            self.zones = self.wizard.zona_service.listar_zonas(
                self.wizard.esquema_cotizacion_id
            )
            self.channels = self.wizard.zona_service.listar_canales()
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo cargar", message=str(exc), parent=self.wizard)
            return

        self.zone_by_id = {zone.zona_id: zone for zone in self.zones}
        self.zone_list.delete(0, tk.END)
        for zone in self.zones:
            self.zone_list.insert(tk.END, zone.nombre)
        self._refresh_matrix()

    def _refresh_matrix(self) -> None:
        columns = ["zona", *[f"canal_{c.canal_selectividad_id}" for c in self.channels]]
        self.channel_by_column = {f"canal_{c.canal_selectividad_id}": c for c in self.channels}
        self.table.configure(columns=columns)
        self.table.heading("zona", text="Zona")
        self.table.column("zona", width=180, anchor=tk.W)

        for channel in self.channels:
            name = f"canal_{channel.canal_selectividad_id}"
            self.table.heading(name, text=channel.nombre)
            self.table.column(name, width=135, anchor=tk.E)

        children = self.table.get_children()
        if children:
            self.table.delete(*children)

        apply_treeview_row_tags(self.table)

        for idx, zone in enumerate(self.zones):
            tariffs = {item.canal_selectividad_id: item for item in zone.tarifas_por_canal}
            values = [zone.nombre]
            for channel in self.channels:
                tariff = tariffs.get(channel.canal_selectividad_id)
                values.append(self.format_amount(tariff.monto) if tariff else "")
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.table.insert("", tk.END, iid=str(zone.zona_id), values=values, tags=(tag,))


    def new_zone(self) -> None:
        if not self.wizard.editable:
            return
        dialog = ZonaDialog(
            parent=self.wizard,
            service=self.wizard.zona_service,
            esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
        )
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.refresh()

    def edit_zone(self) -> None:
        selected = self.zone_list.curselection()
        if not selected:
            messagebox.showinfo(title="Seleccionar zona", message="Selecciona una zona.", parent=self.wizard)
            return
        zone = self.zones[selected[0]]
        dialog = ZonaDialog(
            parent=self.wizard,
            service=self.wizard.zona_service,
            esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
            zona=zone,
        )
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.refresh()

    def delete_zone(self) -> None:
        selected = self.zone_list.curselection()
        if not selected:
            messagebox.showinfo(title="Seleccionar zona", message="Selecciona una zona.", parent=self.wizard)
            return
        zone = self.zones[selected[0]]
        if len(self.zones) == 1:
            messagebox.showwarning(
                title="Última zona",
                message="El esquema debe conservar al menos una zona. Renombra GENERAL si corresponde.",
                parent=self.wizard,
            )
            return
        if not messagebox.askyesno(title="Eliminar zona", message=f"¿Eliminar {zone.nombre} y sus tarifas?", parent=self.wizard):
            return
        try:
            self.wizard.zona_service.eliminar_zona(zone.zona_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self.wizard)
            return
        self.refresh()

    def _selection_from_event(self, event):
        if self.table.identify_region(event.x, event.y) != "cell":
            return None
        row_id = self.table.identify_row(event.y)
        column_id = self.table.identify_column(event.x)
        if not row_id:
            return None
        try:
            column_index = int(column_id.removeprefix("#")) - 1
            zone = self.zone_by_id[int(row_id)]
        except (ValueError, KeyError):
            return None
        columns = list(self.table["columns"])
        if column_index < 0 or column_index >= len(columns):
            return None
        column = columns[column_index]
        if column == "zona":
            return None
        channel = self.channel_by_column.get(column)
        return (zone, channel) if channel else None

    def _table_click(self, event) -> None:
        selection = self._selection_from_event(event)
        if selection is None:
            return
        zone, channel = selection
        self.selected_zone_id = zone.zona_id
        self.selected_channel_id = channel.canal_selectividad_id
        self.selection_var.set(f"Seleccionada: {zone.nombre} × {channel.nombre}")

    def _table_double_click(self, event) -> str:
        selection = self._selection_from_event(event)
        if selection is None:
            return "break"
        zone, channel = selection
        self.selected_zone_id = zone.zona_id
        self.selected_channel_id = channel.canal_selectividad_id
        self.selection_var.set(
            f"Seleccionada: {zone.nombre} × {channel.nombre}"
        )
        self.after_idle(self.edit_tariff)
        return "break"

    def _current_selection(self):
        zone = self.zone_by_id.get(self.selected_zone_id)
        channel = next((c for c in self.channels if c.canal_selectividad_id == self.selected_channel_id), None)
        if zone is None or channel is None:
            messagebox.showinfo(title="Seleccionar tarifa", message="Haz clic sobre una celda de canal.", parent=self.wizard)
            return None
        return zone, channel

    def edit_tariff(self) -> None:
        selection = self._current_selection()
        if selection is None:
            return
        zone, channel = selection
        tariff = self._find_tariff(zone, channel)
        dialog = MontoTarifaDialog(
            parent=self.wizard,
            service=self.wizard.zona_service,
            esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
            zona_id=zone.zona_id,
            canal_selectividad_id=channel.canal_selectividad_id,
            zona_nombre=zone.nombre,
            canal_nombre=channel.nombre,
            moneda_codigo=self.wizard.esquema.moneda_codigo,
            monto_actual=tariff.monto if tariff else None,
        )
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.refresh()

    def remove_tariff(self) -> None:
        selection = self._current_selection()
        if selection is None:
            return
        zone, channel = selection
        try:
            self.wizard.zona_service.eliminar_tarifa(
                esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
                zona_id=zone.zona_id,
                canal_selectividad_id=channel.canal_selectividad_id,
            )
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo quitar", message=str(exc), parent=self.wizard)
            return
        self.refresh()

    @staticmethod
    def _find_tariff(zone: Zona, channel: CanalSelectividad) -> TarifaZonaCanalSelectividad | None:
        return next((item for item in zone.tarifas_por_canal if item.canal_selectividad_id == channel.canal_selectividad_id), None)


class TrucksStep(WizardStep):
    def __init__(self, parent: tk.Misc, wizard: EsquemaWizardWindow) -> None:
        super().__init__(parent, wizard)

        self.tramos: list[AdicionalCamiones] = []
        self.zones: list[Zona] = []
        self.tramo_by_id = {}
        self.zone_by_column = {}
        self.selected_tramo_id = None
        self.selected_zone_id = None
        self.selection_var = tk.StringVar(value="Ninguna tarifa seleccionada.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="3. Adicionales por camiones", style="SectionTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(self, text="Componente opcional. Si no corresponde, pulsa Siguiente.").grid(row=1, column=0, sticky="w", pady=(0, 12))

        body = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        body.grid(row=2, column=0, sticky="nsew")
        left = ttk.Frame(body, padding=10)
        right = ttk.Frame(body, padding=10)
        body.add(left, weight=1)
        body.add(right, weight=4)

        ttk.Label(left, text="Tramos", style="SectionTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.tramos_list = tk.Listbox(left, exportselection=False)
        self.tramos_list.pack(fill=tk.BOTH, expand=True)
        self.tramos_list.bind("<Double-1>", lambda _event: self.edit_tramo())
        ttk.Button(left, text="Nuevo tramo", command=self.new_tramo).pack(fill=tk.X, pady=(8, 5))
        ttk.Button(left, text="Editar tramo", command=self.edit_tramo).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(left, text="Eliminar tramo", command=self.delete_tramo).pack(fill=tk.X)

        ttk.Label(right, text="Matriz Tramo × Zona", style="SectionTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        table_frame = ttk.Frame(right)
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, show="headings", selectmode="browse")
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.bind("<Button-1>", self._table_click)
        self.table.bind("<Double-1>", self._table_double_click)
        ybar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        ybar.grid(row=0, column=1, sticky="ns")
        xbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        xbar.grid(row=1, column=0, sticky="ew")
        self.table.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        ttk.Label(right, textvariable=self.selection_var).pack(fill=tk.X, pady=(8, 0))
        actions = ttk.Frame(right)
        actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(actions, text="Editar tarifa", command=self.edit_tariff).pack(side=tk.LEFT)
        ttk.Button(actions, text="Quitar tarifa", command=self.remove_tariff).pack(side=tk.LEFT, padx=(8, 0))

    def refresh(self) -> None:
        if self.wizard.esquema_cotizacion_id is None:
            return
        try:
            self.tramos = self.wizard.camiones_service.listar_tramos(self.wizard.esquema_cotizacion_id)
            self.zones = self.wizard.zona_service.listar_zonas(self.wizard.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo cargar", message=str(exc), parent=self.wizard)
            return
        self.tramo_by_id = {item.adicional_camiones_id: item for item in self.tramos}
        self.tramos_list.delete(0, tk.END)
        for item in self.tramos:
            self.tramos_list.insert(tk.END, item.descripcion_rango)
        self._refresh_matrix()

    def _refresh_matrix(self) -> None:
        columns = ["tramo", *[f"zona_{z.zona_id}" for z in self.zones]]
        self.zone_by_column = {f"zona_{z.zona_id}": z for z in self.zones}
        self.table.configure(columns=columns)
        self.table.heading("tramo", text="Tramo")
        self.table.column("tramo", width=190, anchor=tk.W)
        for zone in self.zones:
            name = f"zona_{zone.zona_id}"
            self.table.heading(name, text=zone.nombre)
            self.table.column(name, width=140, anchor=tk.E)
        children = self.table.get_children()
        if children:
            self.table.delete(*children)
        apply_treeview_row_tags(self.table)
        for idx, tramo in enumerate(self.tramos):
            tariffs = {item.zona_id: item for item in tramo.tarifas_por_zona}
            values = [tramo.descripcion_rango]
            for zone in self.zones:
                tariff = tariffs.get(zone.zona_id)
                values.append(self.format_amount(tariff.monto) if tariff else "")
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.table.insert("", tk.END, iid=str(tramo.adicional_camiones_id), values=values, tags=(tag,))


    def new_tramo(self) -> None:
        dialog = TramoCamionesDialog(parent=self.wizard, service=self.wizard.camiones_service, esquema_cotizacion_id=self.wizard.esquema_cotizacion_id)
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.refresh()

    def edit_tramo(self) -> None:
        selected = self.tramos_list.curselection()
        if not selected:
            messagebox.showinfo(title="Seleccionar tramo", message="Selecciona un tramo.", parent=self.wizard)
            return
        tramo = self.tramos[selected[0]]
        dialog = TramoCamionesDialog(parent=self.wizard, service=self.wizard.camiones_service, esquema_cotizacion_id=self.wizard.esquema_cotizacion_id, tramo=tramo)
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.refresh()

    def delete_tramo(self) -> None:
        selected = self.tramos_list.curselection()
        if not selected:
            messagebox.showinfo(title="Seleccionar tramo", message="Selecciona un tramo.", parent=self.wizard)
            return
        tramo = self.tramos[selected[0]]
        if not messagebox.askyesno(title="Eliminar tramo", message=f"¿Eliminar {tramo.descripcion_rango}?", parent=self.wizard):
            return
        try:
            self.wizard.camiones_service.eliminar_tramo(tramo.adicional_camiones_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self.wizard)
            return
        self.refresh()

    def _selection_from_event(self, event):
        if self.table.identify_region(event.x, event.y) != "cell":
            return None
        row_id = self.table.identify_row(event.y)
        column_id = self.table.identify_column(event.x)
        try:
            column_index = int(column_id.removeprefix("#")) - 1
            tramo = self.tramo_by_id[int(row_id)]
        except (ValueError, KeyError):
            return None
        columns = list(self.table["columns"])
        if column_index < 0 or column_index >= len(columns):
            return None
        column = columns[column_index]
        if column == "tramo":
            return None
        zone = self.zone_by_column.get(column)
        return (tramo, zone) if zone else None

    def _table_click(self, event) -> None:
        selection = self._selection_from_event(event)
        if selection is None:
            return
        tramo, zone = selection
        self.selected_tramo_id = tramo.adicional_camiones_id
        self.selected_zone_id = zone.zona_id
        self.selection_var.set(f"Seleccionada: {tramo.descripcion_rango} × {zone.nombre}")

    def _table_double_click(self, event) -> str:
        selection = self._selection_from_event(event)
        if selection is None:
            return "break"
        tramo, zone = selection
        self.selected_tramo_id = tramo.adicional_camiones_id
        self.selected_zone_id = zone.zona_id
        self.selection_var.set(
            f"Seleccionada: {tramo.descripcion_rango} × {zone.nombre}"
        )
        self.after_idle(self.edit_tariff)
        return "break"

    def _current_selection(self):
        tramo = self.tramo_by_id.get(self.selected_tramo_id)
        zone = next((z for z in self.zones if z.zona_id == self.selected_zone_id), None)
        if tramo is None or zone is None:
            messagebox.showinfo(title="Seleccionar tarifa", message="Haz clic sobre una celda de zona.", parent=self.wizard)
            return None
        return tramo, zone

    def edit_tariff(self) -> None:
        selection = self._current_selection()
        if selection is None:
            return
        tramo, zone = selection
        tariff = self._find_tariff(tramo, zone)
        dialog = MontoCamionesZonaDialog(
            parent=self.wizard,
            service=self.wizard.camiones_service,
            esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
            adicional_camiones_id=tramo.adicional_camiones_id,
            zona_id=zone.zona_id,
            tramo_descripcion=tramo.descripcion_rango,
            zona_nombre=zone.nombre,
            moneda_codigo=self.wizard.esquema.moneda_codigo,
            monto_actual=tariff.monto if tariff else None,
        )
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.refresh()

    def remove_tariff(self) -> None:
        selection = self._current_selection()
        if selection is None:
            return
        tramo, zone = selection
        try:
            self.wizard.camiones_service.eliminar_tarifa(
                esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
                adicional_camiones_id=tramo.adicional_camiones_id,
                zona_id=zone.zona_id,
            )
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo quitar", message=str(exc), parent=self.wizard)
            return
        self.refresh()

    @staticmethod
    def _find_tariff(tramo: AdicionalCamiones, zone: Zona) -> TarifaAdicionalCamionesZona | None:
        return next((item for item in tramo.tarifas_por_zona if item.zona_id == zone.zona_id), None)


class ScheduleStep(WizardStep):
    DAYS = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado", 7: "Domingo"}

    def __init__(self, parent: tk.Misc, wizard: EsquemaWizardWindow) -> None:
        super().__init__(parent, wizard)
        self.catalog = []
        self.tariffs = []
        self.position_by_key = {}
        self.tariff_by_position = {}
        self.selected_ids = set()
        self.selection_var = tk.StringVar(value="Ninguna posición seleccionada.")
        self.status_var = tk.StringVar(value="")
        self.hour_from_var = tk.StringVar(value="00")
        self.hour_to_var = tk.StringVar(value="23")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        ttk.Label(self, text="4. Adicionales por día y hora", style="SectionTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(self, text="Componente opcional. Cada posición conserva un importe independiente.").grid(row=1, column=0, sticky="w", pady=(0, 10))

        controls = ttk.LabelFrame(self, text="Configuración y selección", padding=8)
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(controls, text="Inicializar 168 posiciones", command=self.initialize).grid(row=0, column=0)
        ttk.Button(controls, text="Eliminar configuración", command=self.delete_configuration).grid(row=0, column=1, padx=(8, 16))
        ttk.Label(controls, text="Días").grid(row=0, column=2, sticky="w")
        self.days_list = tk.Listbox(controls, selectmode=tk.EXTENDED, exportselection=False, height=3, width=16)
        self.days_list.grid(row=1, column=2, rowspan=2, sticky="nsew", pady=(4, 0))
        for number in range(1, 8):
            self.days_list.insert(tk.END, self.DAYS[number])
        hours = tuple(f"{hour:02d}" for hour in range(24))
        ttk.Combobox(controls, textvariable=self.hour_from_var, state="readonly", values=hours, width=5).grid(row=1, column=3, padx=(10, 0))
        ttk.Combobox(controls, textvariable=self.hour_to_var, state="readonly", values=hours, width=5).grid(row=1, column=4, padx=(6, 0))
        ttk.Button(controls, text="Seleccionar rango", command=self.select_range).grid(row=1, column=5, padx=(8, 0))
        ttk.Button(controls, text="Semana completa", command=self.select_all).grid(row=1, column=6, padx=(8, 0))
        ttk.Button(controls, text="Limpiar selección", command=self.clear_selection).grid(row=1, column=7, padx=(8, 0))
        controls.columnconfigure(2, weight=1)

        matrix = ttk.Frame(self)
        matrix.grid(row=3, column=0, sticky="nsew")
        matrix.columnconfigure(0, weight=1)
        matrix.rowconfigure(0, weight=1)
        columns = ["dia", *[f"hora_{hour:02d}" for hour in range(24)]]
        self.table = ttk.Treeview(matrix, columns=columns, show="headings", selectmode="none", height=7)
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.bind("<Button-1>", self._table_click)
        xbar = ttk.Scrollbar(matrix, orient=tk.HORIZONTAL, command=self.table.xview)
        xbar.grid(row=1, column=0, sticky="ew")
        self.table.configure(xscrollcommand=xbar.set)
        self.table.heading("dia", text="Día")
        self.table.column("dia", width=105, anchor=tk.W, stretch=False)
        for hour in range(24):
            name = f"hora_{hour:02d}"
            self.table.heading(name, text=f"{hour:02d}:00")
            self.table.column(name, width=80, anchor=tk.E, stretch=False)

        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        actions.columnconfigure(3, weight=1)
        ttk.Button(actions, text="Asignar importe", command=self.assign_amount).grid(row=0, column=0)
        ttk.Button(actions, text="Restablecer a cero", command=self.reset_amount).grid(row=0, column=1, padx=(8, 0))
        ttk.Label(actions, textvariable=self.selection_var).grid(row=0, column=2, sticky="w", padx=(14, 0))
        ttk.Label(actions, textvariable=self.status_var).grid(row=0, column=3, sticky="e")

    def refresh(self) -> None:
        if self.wizard.esquema_cotizacion_id is None:
            return
        try:
            self.catalog = self.wizard.horario_service.listar_catalogo()
            self.tariffs = self.wizard.horario_service.listar(self.wizard.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo cargar", message=str(exc), parent=self.wizard)
            return
        self.position_by_key = {(item.dia, item.hora): item for item in self.catalog}
        self.tariff_by_position = {item.dia_hora_id: item for item in self.tariffs}
        self.selected_ids.intersection_update(self.tariff_by_position)
        self._refresh_matrix()
        self._refresh_labels()

    def _refresh_matrix(self) -> None:
        children = self.table.get_children()
        if children:
            self.table.delete(*children)
        apply_treeview_row_tags(self.table)
        for day in range(1, 8):
            values = [self.DAYS[day]]
            for hour in range(24):
                position = self.position_by_key.get((day, hour))
                tariff = self.tariff_by_position.get(position.dia_hora_id) if position else None
                if tariff is None:
                    values.append("")
                else:
                    value = self.format_amount(tariff.monto)
                    values.append(f"[{value}]" if position.dia_hora_id in self.selected_ids else value)
            tag = "evenrow" if day % 2 == 0 else "oddrow"
            self.table.insert("", tk.END, iid=f"dia_{day}", values=values, tags=(tag,))


    def _table_click(self, event) -> None:
        if self.table.identify_region(event.x, event.y) != "cell":
            return
        try:
            day = int(self.table.identify_row(event.y).removeprefix("dia_"))
            column = int(self.table.identify_column(event.x).removeprefix("#"))
        except ValueError:
            return
        if column <= 1:
            return
        position = self.position_by_key.get((day, column - 2))
        if position is None or position.dia_hora_id not in self.tariff_by_position:
            messagebox.showinfo(title="Configuración no inicializada", message="Inicializa primero las 168 posiciones.", parent=self.wizard)
            return
        position_id = position.dia_hora_id
        if position_id in self.selected_ids:
            self.selected_ids.remove(position_id)
        else:
            self.selected_ids.add(position_id)
        self._refresh_matrix()
        self._refresh_labels()

    def initialize(self) -> None:
        try:
            self.wizard.horario_service.inicializar(self.wizard.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo inicializar", message=str(exc), parent=self.wizard)
            return
        self.refresh()

    def delete_configuration(self) -> None:
        if not self.tariffs:
            return
        if not messagebox.askyesno(title="Eliminar configuración", message="¿Eliminar las 168 posiciones y sus importes?", parent=self.wizard):
            return
        try:
            self.wizard.horario_service.eliminar_configuracion(self.wizard.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self.wizard)
            return
        self.selected_ids.clear()
        self.refresh()

    def select_range(self) -> None:
        selected_days = self.days_list.curselection()
        if not selected_days:
            messagebox.showinfo(title="Seleccionar días", message="Selecciona al menos un día.", parent=self.wizard)
            return
        if len(self.tariffs) != 168:
            messagebox.showinfo(title="Configuración no inicializada", message="Inicializa primero las 168 posiciones.", parent=self.wizard)
            return
        start = int(self.hour_from_var.get())
        end = int(self.hour_to_var.get())
        if end < start:
            messagebox.showwarning(title="Rango inválido", message="La hora hasta no puede ser menor que la hora desde.", parent=self.wizard)
            return
        for list_index in selected_days:
            day = list_index + 1
            for hour in range(start, end + 1):
                position = self.position_by_key.get((day, hour))
                if position:
                    self.selected_ids.add(position.dia_hora_id)
        self._refresh_matrix()
        self._refresh_labels()

    def select_all(self) -> None:
        if len(self.tariffs) != 168:
            return
        self.selected_ids = set(self.tariff_by_position)
        self._refresh_matrix()
        self._refresh_labels()

    def clear_selection(self) -> None:
        self.selected_ids.clear()
        self._refresh_matrix()
        self._refresh_labels()

    def assign_amount(self) -> None:
        if not self.selected_ids:
            messagebox.showinfo(title="Seleccionar posiciones", message="Selecciona al menos una posición.", parent=self.wizard)
            return
        dialog = MontoDiaHoraDialog(
            parent=self.wizard,
            service=self.wizard.horario_service,
            esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
            dia_hora_ids=sorted(self.selected_ids),
            descripcion_seleccion=f"{len(self.selected_ids)} posición(es) seleccionada(s)",
            moneda_codigo=self.wizard.esquema.moneda_codigo,
        )
        self.wizard.wait_window(dialog)
        if dialog.resultado_guardado:
            self.selected_ids.clear()
            self.refresh()

    def reset_amount(self) -> None:
        if not self.selected_ids:
            return
        try:
            self.wizard.horario_service.restablecer_montos(
                esquema_cotizacion_id=self.wizard.esquema_cotizacion_id,
                dia_hora_ids=sorted(self.selected_ids),
            )
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo restablecer", message=str(exc), parent=self.wizard)
            return
        self.selected_ids.clear()
        self.refresh()

    def _refresh_labels(self) -> None:
        self.selection_var.set(f"{len(self.selected_ids)} posición(es) seleccionada(s)")
        positive = sum(1 for item in self.tariffs if item.monto > Decimal("0.00"))
        self.status_var.set(f"{len(self.tariffs)} posiciones | {positive} con importe > 0")


class ReviewStep(WizardStep):
    def __init__(self, parent: tk.Misc, wizard: EsquemaWizardWindow) -> None:
        super().__init__(parent, wizard)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="5. Revisión", style="SectionTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(self, text="Vista de solo lectura. Finalizar no cambia el estado BORRADOR.").grid(row=1, column=0, sticky="w", pady=(0, 12))

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.tabs = []
        for name in ("General", "Tarifas", "Camiones", "Día y hora", "Comprobación"):
            tab = ttk.Frame(self.notebook, padding=14)
            self.notebook.add(tab, text=name)
            self.tabs.append(tab)

    def refresh(self) -> None:
        if self.wizard.esquema_cotizacion_id is None:
            return
        try:
            summary = self.wizard.resumen_service.obtener(self.wizard.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo cargar el resumen", message=str(exc), parent=self.wizard)
            return
        for tab in self.tabs:
            for child in tab.winfo_children():
                child.destroy()
        self._render_general(self.tabs[0], summary)
        self._render_main_tariffs(self.tabs[1], summary)
        self._render_trucks(self.tabs[2], summary)
        self._render_schedule(self.tabs[3], summary)
        self._render_warnings(self.tabs[4], summary)

    def _render_general(self, tab, summary) -> None:
        general = summary["general"]
        text = (
            f"Esquema: {general['esquema_cotizacion_id']}\n"
            f"Estado: {general['estado']}\n"
            f"Proveedor: {general['proveedor']}\n"
            f"CUIT: {general['cuit']}\n"
            f"Aduana: {general['aduana_codigo']} - {general['aduana_nombre']}\n"
            f"Inicio: {general['fecha_inicio'].strftime('%d/%m/%Y')}\n"
            f"Fin: {general['fecha_fin'].strftime('%d/%m/%Y') if general['fecha_fin'] else 'Sin definir'}\n"
            f"Moneda: {general['moneda_codigo']}\n\n"
            f"Observaciones:\n{general['observaciones'] or 'Sin observaciones.'}"
        )
        ttk.Label(tab, text=text, justify=tk.LEFT, wraplength=1000).pack(anchor=tk.W)

    def _render_main_tariffs(self, tab, summary) -> None:
        channels = summary["canales"]
        rows = summary["tarifas_principales"]
        columns = ["zona", *[f"c_{c['canal_selectividad_id']}" for c in channels]]
        table = ttk.Treeview(tab, columns=columns, show="headings")
        table.pack(fill=tk.BOTH, expand=True)
        table.heading("zona", text="Zona")
        table.column("zona", width=200, anchor=tk.W)
        for channel in channels:
            name = f"c_{channel['canal_selectividad_id']}"
            table.heading(name, text=channel["nombre"])
            table.column(name, width=140, anchor=tk.E)
        for row in rows:
            values = [row["zona"]]
            for channel in channels:
                value = row["tarifas"].get(channel["canal_selectividad_id"])
                values.append(self.format_amount(value) if value is not None else "Sin cargar")
            table.insert("", tk.END, values=values)

    def _render_trucks(self, tab, summary) -> None:
        zones = summary["zonas"]
        ranges = summary["tramos_camiones"]
        if not ranges:
            ttk.Label(tab, text="No hay adicionales por camiones configurados.").pack(anchor=tk.W)
            return
        columns = ["tramo", *[f"z_{z['zona_id']}" for z in zones]]
        table = ttk.Treeview(tab, columns=columns, show="headings")
        table.pack(fill=tk.BOTH, expand=True)
        table.heading("tramo", text="Tramo")
        table.column("tramo", width=200, anchor=tk.W)
        for zone in zones:
            name = f"z_{zone['zona_id']}"
            table.heading(name, text=zone["nombre"])
            table.column(name, width=140, anchor=tk.E)
        for item in ranges:
            values = [item["descripcion"]]
            for zone in zones:
                value = item["tarifas"].get(zone["zona_id"])
                values.append(self.format_amount(value) if value is not None else "Sin cargar")
            table.insert("", tk.END, values=values)

    def _render_schedule(self, tab, summary) -> None:
        schedule = summary["horario"]
        ttk.Label(
            tab,
            text=(
                f"Posiciones: {schedule['cantidad_registros']} | "
                f"Importe > 0: {schedule['cantidad_mayor_cero']} | "
                f"En cero: {schedule['cantidad_en_cero']}"
            ),
        ).pack(anchor=tk.W, pady=(0, 10))
        columns = ("dia", "desde", "hasta", "monto")
        table = ttk.Treeview(tab, columns=columns, show="headings")
        table.pack(fill=tk.BOTH, expand=True)
        for name, label in (("dia", "Día"), ("desde", "Desde"), ("hasta", "Hasta"), ("monto", "Importe")):
            table.heading(name, text=label)
        for block in schedule["bloques"]:
            table.insert("", tk.END, values=(block["nombre_dia"], f"{block['hora_desde']:02d}:00", f"{block['hora_hasta']:02d}:00", self.format_amount(block["monto"])))

    def _render_warnings(self, tab, summary) -> None:
        columns = ("nivel", "detalle")
        table = ttk.Treeview(tab, columns=columns, show="headings")
        table.pack(fill=tk.BOTH, expand=True)
        table.heading("nivel", text="Nivel")
        table.heading("detalle", text="Detalle")
        table.column("nivel", width=130)
        table.column("detalle", width=900, anchor=tk.W)
        for item in summary["advertencias"]:
            table.insert("", tk.END, values=(item["nivel"], item["mensaje"]))
