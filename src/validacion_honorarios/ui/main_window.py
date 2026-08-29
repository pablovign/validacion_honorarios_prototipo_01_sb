"""Ventana principal de la aplicación con CustomTkinter y diseño prémium Pizarra/Índigo."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from validacion_honorarios.config import settings
from validacion_honorarios.db.connection import check_database_connection
from validacion_honorarios.services import (
    AduanaService,
    CanalSelectividadService,
    EsquemaCotizacionService,
    ProveedorService,
)
from validacion_honorarios.ui.aduanas_view import AduanasView
from validacion_honorarios.ui.canales_selectividad_view import (
    CanalesSelectividadView,
)
from validacion_honorarios.ui.esquemas_cotizacion_view import (
    EsquemasCotizacionView,
)
from validacion_honorarios.ui.proveedores_view import ProveedoresView
from validacion_honorarios.ui.theme import (
    COLOR_BG_CARD,
    COLOR_BG_MAIN,
    COLOR_BG_SIDEBAR,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    FONT_FAMILY,
    apply_global_ttk_theme,
    get_font,
    setup_theme,
    style_treeview,
)


logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """Ventana principal de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        setup_theme()
        apply_global_ttk_theme(ttk.Style(self))
        style_treeview()

        self.title(f"{settings.app_name} - Gestión de Honorarios")
        self.geometry("1300x800")

        self.minsize(1050, 650)

        # Servicios para métricas del dashboard
        self.aduana_service = AduanaService()
        self.proveedor_service = ProveedorService()
        self.esquema_service = EsquemaCotizacionService()
        self.canal_service = CanalSelectividadService()

        self.current_view: tk.Widget | None = None
        self.active_nav_button: ctk.CTkButton | None = None
        self.nav_buttons: list[ctk.CTkButton] = []

        self._build_interface()
        self._show_home()

    def _build_interface(self) -> None:
        # Configurar layout grid 1x2 (Sidebar + Contenido)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # SIDEBAR (Barra lateral)
        # -------------------------------------------------------------
        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=COLOR_BG_SIDEBAR,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Header con Logo / Título
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill=tk.X, padx=20, pady=(24, 28))

        logo_badge = ctk.CTkLabel(
            brand_frame,
            text="⚖️",
            font=ctk.CTkFont(family=FONT_FAMILY, size=28),
        )
        logo_badge.pack(anchor="w")

        app_title = ctk.CTkLabel(
            brand_frame,
            text="Validación de\nHonorarios",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_LIGHT,
            justify="left",
        )
        app_title.pack(anchor="w", pady=(6, 0))

        app_subtitle = ctk.CTkLabel(
            brand_frame,
            text="SISTEMA DE CONTROL",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color="#818CF8",  # Indigo claro
        )
        app_subtitle.pack(anchor="w", pady=(2, 0))

        # Separador sutil
        sep = ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color="#334155",
        )
        sep.pack(fill=tk.X, padx=20, pady=(0, 16))

        # Contenedor de Botones de Navegación
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill=tk.X, padx=12, expand=True, anchor="n")

        self.btn_home = self._create_nav_button(
            nav_container, "🏠  Inicio", self._show_home
        )
        self.btn_aduanas = self._create_nav_button(
            nav_container, "🛃  Aduanas", self._show_customs_offices
        )
        self.btn_proveedores = self._create_nav_button(
            nav_container, "🏢  Proveedores", self._show_providers
        )
        self.btn_esquemas = self._create_nav_button(
            nav_container, "📋  Esquemas de cotización", self._show_quotes
        )
        self.btn_canales = self._create_nav_button(
            nav_container, "🎯  Canales de selectividad", self._show_channels
        )

        self.nav_buttons = [
            self.btn_home,
            self.btn_aduanas,
            self.btn_proveedores,
            self.btn_esquemas,
            self.btn_canales,
        ]

        # -------------------------------------------------------------
        # FOOTER DEL SIDEBAR (Modo Oscuro + Estado)
        # -------------------------------------------------------------
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=20, side="bottom")

        # Switch de Modo Oscuro / Claro
        theme_frame = ctk.CTkFrame(footer, fg_color="#1E293B", corner_radius=8)
        theme_frame.pack(fill=tk.X, pady=(0, 12), ipady=4, ipadx=8)

        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Modo Oscuro",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_LIGHT,
            progress_color=COLOR_PRIMARY[0],
            command=self._toggle_appearance_mode,
        )
        self.theme_switch.select()  # Dark mode activo por defecto
        self.theme_switch.pack(side="left", padx=10, pady=8)

        # Versión / Entorno
        env_label = ctk.CTkLabel(
            footer,
            text=f"Entorno: {settings.app_env} • v0.1.0",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color="#94A3B8",
        )
        env_label.pack(anchor="w")

        # -------------------------------------------------------------
        # CONTENEDOR PRINCIPAL DE CONTENIDO
        # -------------------------------------------------------------
        self.content_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLOR_BG_MAIN,
        )
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def _create_nav_button(
        self,
        parent: ctk.CTkFrame,
        text: str,
        command: callable,
    ) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            parent,
            text=text,
            anchor="w",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="transparent",
            text_color="#CBD5E1",
            hover_color="#1E293B",
            height=42,
            corner_radius=8,
            command=lambda: self._on_nav_click(btn, command),
        )
        btn.pack(fill=tk.X, pady=4)
        return btn

    def _on_nav_click(self, btn: ctk.CTkButton, command: callable) -> None:
        self._set_active_nav_button(btn)
        command()

    def _set_active_nav_button(self, btn: ctk.CTkButton) -> None:
        self.active_nav_button = btn
        for b in self.nav_buttons:
            if b == btn:
                b.configure(
                    fg_color=COLOR_PRIMARY[0],
                    text_color="#FFFFFF",
                )
            else:
                b.configure(
                    fg_color="transparent",
                    text_color="#CBD5E1",
                )

    def _toggle_appearance_mode(self) -> None:
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="Modo Oscuro")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="Modo Claro")

        # Actualizar estilos globales y de tablas activas
        apply_global_ttk_theme(ttk.Style(self))
        style_treeview()
        if self.current_view is not None and hasattr(self.current_view, "_load_data"):
            self.current_view._load_data()


    def _replace_view(self, view: tk.Widget) -> None:
        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = view
        self.current_view.grid(row=0, column=0, sticky="nsew")
        style_treeview()

    # -------------------------------------------------------------
    # VISTA DE INICIO / DASHBOARD
    # -------------------------------------------------------------
    def _show_home(self) -> None:
        self._set_active_nav_button(self.btn_home)

        scrollable_home = ctk.CTkScrollableFrame(
            self.content_container,
            fg_color=COLOR_BG_MAIN,
            corner_radius=0,
        )

        # Header de Bienvenida
        header_frame = ctk.CTkFrame(
            scrollable_home,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        header_frame.pack(fill=tk.X, padx=28, pady=(28, 20), ipady=12)

        title_lbl = ctk.CTkLabel(
            header_frame,
            text=f"Bienvenido a {settings.app_name}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w", padx=24, pady=(12, 4))

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="Sistema centralizado para administración de aduanas, proveedores y validación de esquemas de cotización.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_lbl.pack(anchor="w", padx=24, pady=(0, 12))

        # -------------------------------------------------------------
        # TARJETAS RESUMEN / METRICAS (KPIs)
        # -------------------------------------------------------------
        kpi_container = ctk.CTkFrame(scrollable_home, fg_color="transparent")
        kpi_container.pack(fill=tk.X, padx=28, pady=(0, 24))
        for i in range(4):
            kpi_container.grid_columnconfigure(i, weight=1, uniform="kpi")

        # Obtener conteos de datos de forma segura
        try:
            total_aduanas = len(self.aduana_service.listar())
        except Exception:
            total_aduanas = 0

        try:
            total_proveedores = len(self.proveedor_service.listar())
        except Exception:
            total_proveedores = 0

        try:
            total_esquemas = len(self.esquema_service.listar())
        except Exception:
            total_esquemas = 0

        try:
            total_canales = len(self.canal_service.listar())
        except Exception:
            total_canales = 0

        self._create_kpi_card(
            kpi_container, 0, "🛃", "Aduanas", str(total_aduanas), self._show_customs_offices
        )
        self._create_kpi_card(
            kpi_container, 1, "🏢", "Proveedores", str(total_proveedores), self._show_providers
        )
        self._create_kpi_card(
            kpi_container, 2, "📋", "Esquemas", str(total_esquemas), self._show_quotes
        )
        self._create_kpi_card(
            kpi_container, 3, "🎯", "Canales", str(total_canales), self._show_channels
        )

        # -------------------------------------------------------------
        # PANEL DE ESTADO DE BASE DE DATOS
        # -------------------------------------------------------------
        db_card = ctk.CTkFrame(
            scrollable_home,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        db_card.pack(fill=tk.X, padx=28, pady=(0, 24), ipady=8)

        db_title = ctk.CTkLabel(
            db_card,
            text="🔌 Estado de la Base de Datos",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        db_title.pack(anchor="w", padx=24, pady=(16, 8))

        status_row = ctk.CTkFrame(db_card, fg_color="transparent")
        status_row.pack(fill=tk.X, padx=24, pady=(0, 16))

        db_status_lbl = ctk.CTkLabel(
            status_row,
            text="Estado: Conexión pendiente de verificación.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLOR_TEXT_MUTED,
        )
        db_status_lbl.pack(side="left")

        def check_connection() -> None:
            db_status_lbl.configure(
                text="Estado: Comprobando conexión con PostgreSQL...",
                text_color=COLOR_PRIMARY[0],
            )
            self.update_idletasks()

            success, message = check_database_connection()

            if success:
                db_status_lbl.configure(
                    text="Estado: Conectado exitosamente a PostgreSQL 🟢",
                    text_color=COLOR_SUCCESS[1],
                )
                messagebox.showinfo(
                    title="Conexión correcta",
                    message=message,
                    parent=self,
                )
            else:
                db_status_lbl.configure(
                    text="Estado: Error de conexión con PostgreSQL 🔴",
                    text_color=COLOR_DANGER[1],
                )
                messagebox.showerror(
                    title="Error de conexión",
                    message=(
                        "No fue posible conectar con PostgreSQL.\n\n"
                        f"Detalle:\n{message}"
                    ),
                    parent=self,
                )

        check_btn = ctk.CTkButton(
            status_row,
            text="Comprobar conexión",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=8,
            height=34,
            command=check_connection,
        )
        check_btn.pack(side="right")

        self._replace_view(scrollable_home)

    def _create_kpi_card(
        self,
        parent: ctk.CTkFrame,
        col: int,
        icon: str,
        title: str,
        value: str,
        action: callable,
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0), sticky="nsew", ipady=12)

        icon_lbl = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(family=FONT_FAMILY, size=24),
        )
        icon_lbl.pack(anchor="w", padx=18, pady=(14, 2))

        val_lbl = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        val_lbl.pack(anchor="w", padx=18)

        title_lbl = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        title_lbl.pack(anchor="w", padx=18, pady=(0, 10))

        open_btn = ctk.CTkButton(
            card,
            text="Ver registros →",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color="transparent",
            text_color=COLOR_PRIMARY,
            hover_color=COLOR_BG_CARD,
            height=28,
            anchor="w",
            command=action,
        )
        open_btn.pack(fill=tk.X, padx=12, pady=(0, 8))

    def _show_customs_offices(self) -> None:
        self._set_active_nav_button(self.btn_aduanas)
        self._replace_view(AduanasView(self.content_container))

    def _show_providers(self) -> None:
        self._set_active_nav_button(self.btn_proveedores)
        self._replace_view(ProveedoresView(self.content_container))

    def _show_quotes(self) -> None:
        self._set_active_nav_button(self.btn_esquemas)
        self._replace_view(EsquemasCotizacionView(self.content_container))

    def _show_channels(self) -> None:
        self._set_active_nav_button(self.btn_canales)
        self._replace_view(CanalesSelectividadView(self.content_container))