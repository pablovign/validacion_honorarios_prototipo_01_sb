"""Sistema de diseño, paleta de colores y tema para la interfaz gráfica.

Paleta: Pizarra & Índigo (Slate & Indigo) con soporte de Dark / Light mode.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# ==========================================
# PALETA DE COLORES (Tuplas: (Modo Claro, Modo Oscuro))
# ==========================================

COLOR_BG_MAIN = ("#F8FAFC", "#0F172A")       # Slate 50 / Slate 900
COLOR_BG_SURFACE = ("#FFFFFF", "#1E293B")    # Blanco / Slate 800
COLOR_BG_CARD = ("#F1F5F9", "#1E293B")       # Slate 100 / Slate 800
COLOR_BG_SIDEBAR = ("#0F172A", "#0B0F19")    # Slate 900 / Slate 950 (Sidebar siempre sofisticado)

COLOR_PRIMARY = ("#4F46E5", "#6366F1")       # Indigo 600 / Indigo 500
COLOR_PRIMARY_HOVER = ("#4338CA", "#4F46E5") # Indigo 700 / Indigo 600
COLOR_SECONDARY = ("#64748B", "#475569")     # Slate 500 / Slate 600
COLOR_SECONDARY_HOVER = ("#475569", "#334155")

COLOR_BORDER = ("#E2E8F0", "#334155")        # Slate 200 / Slate 700

COLOR_TEXT_PRIMARY = ("#0F172A", "#F8FAFC")  # Slate 900 / Slate 50
COLOR_TEXT_MUTED = ("#64748B", "#94A3B8")    # Slate 500 / Slate 400
COLOR_TEXT_LIGHT = "#F8FAFC"                 # Siempre claro (para botones y sidebar)

COLOR_SUCCESS = ("#059669", "#10B981")       # Emerald 600 / Emerald 500
COLOR_SUCCESS_HOVER = ("#047857", "#059669")
COLOR_DANGER = ("#DC2626", "#EF4444")        # Red 600 / Red 500
COLOR_DANGER_HOVER = ("#B91C1C", "#DC2626")
COLOR_WARNING = ("#D97706", "#F59E0B")       # Amber 600 / Amber 500

# ==========================================
# TIPOGRAFÍAS
# ==========================================

FONT_FAMILY = "Segoe UI"

def get_font(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


# ==========================================
# GESTIÓN Y ESTILIZACIÓN DE COMPONENTES
# ==========================================

def setup_theme() -> None:
    """Configura el tema inicial de CustomTkinter."""
    ctk.set_appearance_mode("Dark")  # Inicia por defecto en Dark Mode elegante
    ctk.set_default_color_theme("blue")


def style_treeview(style: ttk.Style | None = None) -> ttk.Style:
    """Configura el estilo de ttk.Treeview según el modo de apariencia actual."""
    if style is None:
        style = ttk.Style()

    mode = ctk.get_appearance_mode()
    is_dark = mode == "Dark"

    bg_color = "#1E293B" if is_dark else "#FFFFFF"
    fg_color = "#F8FAFC" if is_dark else "#0F172A"
    heading_bg = "#0F172A" if is_dark else "#E2E8F0"
    heading_fg = "#F8FAFC" if is_dark else "#0F172A"
    selected_bg = "#4F46E5"
    selected_fg = "#FFFFFF"

    # Usar clam para permitir customización completa
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        "Custom.Treeview",
        background=bg_color,
        foreground=fg_color,
        fieldbackground=bg_color,
        bordercolor="#334155" if is_dark else "#E2E8F0",
        borderwidth=0,
        font=(FONT_FAMILY, 10),
        rowheight=32,
    )

    style.map(
        "Custom.Treeview",
        background=[("selected", selected_bg)],
        foreground=[("selected", selected_fg)],
    )

    style.configure(
        "Custom.Treeview.Heading",
        background=heading_bg,
        foreground=heading_fg,
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=1,
        relief="flat",
        padding=(8, 6),
    )

    style.map(
        "Custom.Treeview.Heading",
        background=[("active", "#334155" if is_dark else "#CBD5E1")],
    )

    return style
