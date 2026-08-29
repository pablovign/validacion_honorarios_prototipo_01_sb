"""Listado y administración moderna de esquemas de cotización con CustomTkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from validacion_honorarios.db.models import Aduana, Proveedor
from validacion_honorarios.services import (
    ApplicationError,
    EsquemaCotizacionService,
)
from validacion_honorarios.ui.esquema_wizard_window import EsquemaWizardWindow
from validacion_honorarios.ui.resumen_esquema_window import ResumenEsquemaWindow
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
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_WARNING,
    FONT_FAMILY,
    apply_treeview_row_tags,
    style_treeview,
)


class EsquemasCotizacionView(ctk.CTkFrame):
    """Listado y acceso al asistente de esquemas de cotización."""

    ALL_PROVIDERS = "Todos los proveedores"
    ALL_CUSTOMS = "Todas las aduanas"
    ALL_STATES = "Todos los estados"
    ALL_CURRENCIES = "Todas las monedas"

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)

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
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill=tk.X, padx=28, pady=(24, 14))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_frame,
            text="📋 Esquemas de Cotización",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_frame,
            text="Gestiona y valida esquemas de tarifas aduaneras, camiones y adicionales.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_lbl.pack(anchor="w")

        btn_nuevo = ctk.CTkButton(
            header,
            text="+ Nuevo esquema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._new_quote,
        )
        btn_nuevo.pack(side="right")

        # Filtros
        filter_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        filter_card.pack(fill=tk.X, padx=28, pady=(0, 16), ipady=4)

        filters_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filters_inner.pack(fill=tk.X, padx=16, pady=12)

        # Fila 1 de Filtros
        filters_inner.grid_columnconfigure(0, weight=2)
        filters_inner.grid_columnconfigure(1, weight=2)
        filters_inner.grid_columnconfigure(2, weight=2)

        lbl_s = ctk.CTkLabel(filters_inner, text="Buscar:", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED)
        lbl_s.grid(row=0, column=0, sticky="w", padx=4)
        self.search_entry = ctk.CTkEntry(
            filters_inner,
            textvariable=self.search_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            placeholder_text="Buscar por proveedor o CUIT...",
            height=32,
            corner_radius=6,
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 8))
        self.search_entry.bind("<Return>", lambda _e: self._load_data())

        lbl_p = ctk.CTkLabel(filters_inner, text="Proveedor:", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED)
        lbl_p.grid(row=0, column=1, sticky="w", padx=4)
        self.provider_filter = ctk.CTkOptionMenu(
            filters_inner,
            variable=self.provider_filter_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=32,
            corner_radius=6,
            command=lambda _v: self._load_data(),
        )
        self.provider_filter.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 8))

        lbl_a = ctk.CTkLabel(filters_inner, text="Aduana:", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED)
        lbl_a.grid(row=0, column=2, sticky="w", padx=4)
        self.customs_filter = ctk.CTkOptionMenu(
            filters_inner,
            variable=self.customs_filter_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=32,
            corner_radius=6,
            command=lambda _v: self._load_data(),
        )
        self.customs_filter.grid(row=1, column=2, sticky="ew", padx=4, pady=(2, 8))

        # Fila 2 de Filtros
        lbl_est = ctk.CTkLabel(filters_inner, text="Estado:", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED)
        lbl_est.grid(row=2, column=0, sticky="w", padx=4)
        self.state_filter = ctk.CTkOptionMenu(
            filters_inner,
            variable=self.state_filter_var,
            values=[self.ALL_STATES, "BORRADOR", "APROBADO", "RECHAZADO"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=32,
            corner_radius=6,
            command=lambda _v: self._load_data(),
        )
        self.state_filter.grid(row=3, column=0, sticky="ew", padx=4)

        lbl_m = ctk.CTkLabel(filters_inner, text="Moneda:", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED)
        lbl_m.grid(row=2, column=1, sticky="w", padx=4)
        self.currency_filter = ctk.CTkOptionMenu(
            filters_inner,
            variable=self.currency_filter_var,
            values=[self.ALL_CURRENCIES, "ARS", "USD"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY_HOVER,
            button_hover_color=COLOR_PRIMARY_HOVER,
            height=32,
            corner_radius=6,
            command=lambda _v: self._load_data(),
        )
        self.currency_filter.grid(row=3, column=1, sticky="ew", padx=4)

        # Botones de Filtro
        f_btn_frame = ctk.CTkFrame(filters_inner, fg_color="transparent")
        f_btn_frame.grid(row=3, column=2, sticky="e", padx=4)

        btn_aplicar = ctk.CTkButton(
            f_btn_frame,
            text="Filtrar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=6,
            height=32,
            width=70,
            command=self._load_data,
        )
        btn_aplicar.pack(side="left")

        btn_limpiar = ctk.CTkButton(
            f_btn_frame,
            text="Limpiar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=6,
            height=32,
            width=70,
            command=self._clear_filters,
        )
        btn_limpiar.pack(side="left", padx=(6, 0))

        # Contenedor de la Tabla
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        table_card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))

        table_inner = ctk.CTkFrame(table_card, fg_color="transparent")
        table_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        table_inner.rowconfigure(0, weight=1)

        table_inner.columnconfigure(0, weight=1)

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
            table_inner,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
        )

        headings = {
            "id": "ID",
            "proveedor": "PROVEEDOR",
            "cuit": "CUIT",
            "aduana": "ADUANA",
            "inicio": "INICIO",
            "fin": "FIN",
            "estado": "ESTADO",
            "moneda": "MONEDA",
            "zonas": "ZONAS",
            "tramos": "TRAMOS",
            "horario": "HORARIO",
        }

        for column, heading in headings.items():
            self.table.heading(column, text=heading)

        widths = {
            "id": 60,
            "proveedor": 220,
            "cuit": 110,
            "aduana": 160,
            "inicio": 90,
            "fin": 90,
            "estado": 100,
            "moneda": 70,
            "zonas": 60,
            "tramos": 65,
            "horario": 75,
        }

        for column, width in widths.items():
            anchor = tk.W if column in ("proveedor", "aduana") else tk.CENTER
            self.table.column(
                column,
                width=width,
                anchor=anchor,
                stretch=column in ("proveedor", "aduana"),
            )

        ybar = ttk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.table.yview)
        xbar = ttk.Scrollbar(table_inner, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")

        self.table.bind("<Double-1>", lambda _e: self._primary_action())

        # Barra Inferior de Acciones
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=28, pady=(0, 24))

        self.status_label = ctk.CTkLabel(
            action_bar,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.pack(side="left")

        # Botones Principales a la izquierda
        btn_refresh = ctk.CTkButton(
            action_bar,
            text="🔄 Actualizar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=6,
            height=34,
            command=self._refresh_all,
        )
        btn_refresh.pack(side="left", padx=(16, 0))

        btn_continuar = ctk.CTkButton(
            action_bar,
            text="⚡ Continuar asistente",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=6,
            height=34,
            command=self._continue_quote,
        )
        btn_continuar.pack(side="left", padx=(8, 0))

        btn_resumen = ctk.CTkButton(
            action_bar,
            text="📄 Ver resumen",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_BG_CARD,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            corner_radius=6,
            height=34,
            command=self._show_summary,
        )
        btn_resumen.pack(side="left", padx=(8, 0))

        # Botones de Destrucción / Modificación a la derecha
        btn_eliminar = ctk.CTkButton(
            action_bar,
            text="Eliminar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            corner_radius=6,
            height=34,
            command=self._delete_quote,
        )
        btn_eliminar.pack(side="right", padx=(8, 0))

        btn_rechazar = ctk.CTkButton(
            action_bar,
            text="Rechazar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_WARNING,
            hover_color=COLOR_WARNING,
            corner_radius=6,
            height=34,
            command=self._reject_quote,
        )
        btn_rechazar.pack(side="right", padx=(8, 0))

        btn_editar = ctk.CTkButton(
            action_bar,
            text="Editar cabecera",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            corner_radius=6,
            height=34,
            command=self._edit_quote,
        )
        btn_editar.pack(side="right")

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
        style_treeview()
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

        apply_treeview_row_tags(self.table)

        for idx, scheme in enumerate(schemes):
            provider_obj = scheme.proveedor
            customs_obj = provider_obj.aduana
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.table.insert(
                "",
                tk.END,
                iid=str(scheme.esquema_cotizacion_id),
                values=(
                    scheme.esquema_cotizacion_id,
                    provider_obj.razon_social,
                    provider_obj.cuit,
                    f"{customs_obj.codigo} - {customs_obj.nombre}",
                    scheme.fecha_inicio.strftime("%d/%m/%Y"),
                    scheme.fecha_fin.strftime("%d/%m/%Y") if scheme.fecha_fin else "",
                    scheme.estado,
                    scheme.moneda_codigo,
                    len(scheme.zonas),
                    len(scheme.adicionales_camiones),
                    "Sí" if scheme.tarifas_adicionales_dia_hora else "No",
                ),
                tags=(tag,),
            )

        count = len(schemes)

        self.status_label.configure(text=f"Total: {count} {'esquema' if count == 1 else 'esquemas'} encontrados")

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
            messagebox.showwarning(
                title="No hay proveedores",
                message="Registra al menos un proveedor antes de crear un esquema.",
                parent=self,
            )
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
        if not messagebox.askyesno(
            title="Eliminar esquema",
            message=f"¿Eliminar el borrador {scheme.esquema_cotizacion_id} y todos sus datos?",
            parent=self,
        ):
            return
        try:
            self.service.eliminar(scheme.esquema_cotizacion_id)
        except ApplicationError as exc:
            messagebox.showwarning(title="No se pudo eliminar", message=str(exc), parent=self)
            return
        self._refresh_all()
