"""Sistema de diseño global, paleta Pizarra & Índigo y estilos para CustomTkinter y TTK."""

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
COLOR_BG_SIDEBAR = ("#0F172A", "#0B0F19")    # Slate 900 / Slate 950

COLOR_PRIMARY = ("#4F46E5", "#6366F1")       # Indigo 600 / Indigo 500
COLOR_PRIMARY_HOVER = ("#4338CA", "#4F46E5") # Indigo 700 / Indigo 600
COLOR_SECONDARY = ("#64748B", "#475569")     # Slate 500 / Slate 600
COLOR_SECONDARY_HOVER = ("#475569", "#334155")

COLOR_BORDER = ("#E2E8F0", "#334155")        # Slate 200 / Slate 700

COLOR_TEXT_PRIMARY = ("#0F172A", "#F8FAFC")  # Slate 900 / Slate 50
COLOR_TEXT_MUTED = ("#64748B", "#94A3B8")    # Slate 500 / Slate 400
COLOR_TEXT_LIGHT = "#F8FAFC"                 # Siempre claro

COLOR_SUCCESS = ("#059669", "#10B981")       # Emerald 600 / Emerald 500
COLOR_SUCCESS_HOVER = ("#047857", "#059669")
COLOR_DANGER = ("#DC2626", "#EF4444")        # Red 600 / Red 500
COLOR_DANGER_HOVER = ("#B91C1C", "#DC2626")
COLOR_WARNING = ("#D97706", "#F59E0B")       # Amber 600 / Amber 500

FONT_FAMILY = "Segoe UI"

def get_font(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


# ==========================================
# GESTIÓN Y ESTILIZACIÓN GLOBAL DE COMPONENTES
# ==========================================

def setup_theme() -> None:
    """Configura el tema inicial de CustomTkinter y aplica estilos globales a TTK."""
    ctk.set_appearance_mode("Dark")  # Inicia por defecto en Dark Mode elegante
    ctk.set_default_color_theme("blue")
    apply_global_ttk_theme()


def apply_global_ttk_theme(style: ttk.Style | None = None) -> ttk.Style:
    """Aplica de forma global la paleta corporativa Pizarra & Índigo a todos los widgets TTK."""
    if style is None:
        style = ttk.Style()

    mode = ctk.get_appearance_mode()
    is_dark = mode == "Dark"

    bg_main = "#0F172A" if is_dark else "#F8FAFC"
    bg_surface = "#1E293B" if is_dark else "#FFFFFF"
    bg_card = "#1E293B" if is_dark else "#F1F5F9"
    border_color = "#334155" if is_dark else "#CBD5E1"
    fg_text = "#F8FAFC" if is_dark else "#0F172A"
    fg_muted = "#94A3B8" if is_dark else "#64748B"
    primary_color = "#6366F1" if is_dark else "#4F46E5"
    primary_hover = "#4F46E5" if is_dark else "#4338CA"
    danger_color = "#EF4444" if is_dark else "#DC2626"

    # Usar 'clam' como base para permitir coloreado completo
    if "clam" in style.theme_names():
        style.theme_use("clam")

    # 1. Frames y Contenedores
    style.configure("TFrame", background=bg_main)
    style.configure("Surface.TFrame", background=bg_surface)
    style.configure("Card.TFrame", background=bg_card)

    # 2. Etiquetas (Labels)
    style.configure(
        "TLabel",
        background=bg_main,
        foreground=fg_text,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Surface.TLabel",
        background=bg_surface,
        foreground=fg_text,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Muted.TLabel",
        background=bg_main,
        foreground=fg_muted,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Title.TLabel",
        background=bg_main,
        foreground=fg_text,
        font=(FONT_FAMILY, 18, "bold"),
    )
    style.configure(
        "SectionTitle.TLabel",
        background=bg_main,
        foreground=fg_text,
        font=(FONT_FAMILY, 15, "bold"),
    )

    # 3. LabelFrames (Recuadros de sección)
    style.configure(
        "TLabelframe",
        background=bg_surface,
        bordercolor=border_color,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=bg_surface,
        foreground=fg_text,
        font=(FONT_FAMILY, 11, "bold"),
    )

    # 4. Botones TTK
    style.configure(
        "TButton",
        background=primary_color,
        foreground="#FFFFFF",
        relief="flat",
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=0,
        padding=(14, 7),
    )
    style.map(
        "TButton",
        background=[
            ("disabled", "#334155" if is_dark else "#E2E8F0"),
            ("pressed", primary_hover),
            ("active", primary_hover),
        ],
        foreground=[
            ("disabled", "#64748B" if is_dark else "#94A3B8"),
            ("active", "#FFFFFF"),
        ],
    )

    style.configure(
        "Primary.TButton",
        background=primary_color,
        foreground="#FFFFFF",
        relief="flat",
        font=(FONT_FAMILY, 10, "bold"),
        padding=(14, 8),
    )
    style.map(
        "Primary.TButton",
        background=[("active", primary_hover), ("pressed", primary_hover)],
    )

    style.configure(
        "Secondary.TButton",
        background="#334155" if is_dark else "#64748B",
        foreground="#FFFFFF",
        relief="flat",
        font=(FONT_FAMILY, 10),
        padding=(12, 6),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#475569" if is_dark else "#475569")],
    )

    style.configure(
        "Danger.TButton",
        background=danger_color,
        foreground="#FFFFFF",
        relief="flat",
        font=(FONT_FAMILY, 10, "bold"),
        padding=(12, 6),
    )

    # 5. Inputs y Entradas (TEntry)
    style.configure(
        "TEntry",
        fieldbackground=bg_surface,
        foreground=fg_text,
        bordercolor=border_color,
        lightcolor=primary_color,
        darkcolor=primary_color,
        insertcolor=fg_text,
        padding=(8, 6),
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", primary_color)],
        fieldbackground=[("disabled", "#0F172A" if is_dark else "#F1F5F9")],
    )

    # 6. Comboboxes
    style.configure(
        "TCombobox",
        fieldbackground=bg_surface,
        background=bg_surface,
        foreground=fg_text,
        bordercolor=border_color,
        arrowcolor=fg_text,
        arrowsize=14,
        padding=(6, 4),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", bg_surface), ("focus", bg_surface)],
        bordercolor=[("focus", primary_color)],
        foreground=[("readonly", fg_text)],
    )

    # 7. Notebooks (Pestañas)
    style.configure(
        "TNotebook",
        background=bg_main,
        borderwidth=0,
        tabmargins=[2, 5, 2, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=bg_surface,
        foreground=fg_text,
        padding=(16, 8),
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=1,
        bordercolor=border_color,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", primary_color), ("active", primary_hover)],
        foreground=[("selected", "#FFFFFF"), ("active", "#FFFFFF")],
    )

    # 8. Tablas Treeview
    style.configure(
        "Treeview",
        background=bg_surface,
        foreground=fg_text,
        fieldbackground=bg_surface,
        bordercolor=border_color,
        borderwidth=0,
        font=(FONT_FAMILY, 10),
        rowheight=32,
    )
    style.map(
        "Treeview",
        background=[("selected", primary_color)],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure(
        "Treeview.Heading",
        background="#0B0F19" if is_dark else "#E2E8F0",
        foreground=fg_text,
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=1,
        relief="flat",
        padding=(8, 6),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#1E293B" if is_dark else "#CBD5E1")],
    )

    style.configure(
        "Custom.Treeview",
        background=bg_surface,
        foreground=fg_text,
        fieldbackground=bg_surface,
        bordercolor=border_color,
        borderwidth=0,
        font=(FONT_FAMILY, 10),
        rowheight=32,
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", primary_color)],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure(
        "Custom.Treeview.Heading",
        background="#0B0F19" if is_dark else "#E2E8F0",
        foreground=fg_text,
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=1,
        relief="flat",
        padding=(8, 6),
    )
    style.map(
        "Custom.Treeview.Heading",
        background=[("active", "#1E293B" if is_dark else "#CBD5E1")],
    )

    # 9. Scrollbars
    style.configure(
        "Vertical.TScrollbar",
        background=bg_surface,
        troughcolor=bg_main,
        bordercolor=border_color,
        arrowcolor=fg_text,
        relief="flat",
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=bg_surface,
        troughcolor=bg_main,
        bordercolor=border_color,
        arrowcolor=fg_text,
        relief="flat",
    )

    return style


def style_treeview(style: ttk.Style | None = None) -> ttk.Style:
    """Alias para aplicar el tema global."""
    return apply_global_ttk_theme(style)
