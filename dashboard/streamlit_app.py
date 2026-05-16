"""
Facturase — Dashboard Streamlit
Sistema de auditoria inteligente de facturas automotrices con IA.
"""
from __future__ import annotations

import json
import sys
import os
import random
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px

from app.database import (
    init_db,
    listar_auditorias,
    listar_siniestros,
    obtener_siniestro,
    crear_siniestro,
    eliminar_siniestro,
    listar_tarifario,
    agregar_item_tarifario,
    eliminar_item_tarifario,
    verificar_usuario,
    listar_usuarios_count,
    agregar_a_cola,
    listar_cola,
    actualizar_estado_cola,
    eliminar_de_cola,
    limpiar_cola_completados,
    create_session,
    validate_session,
    delete_session,
)
from app.orquestador import auditar_factura
from data.demo_data import FACTURAS_DEMO, DEMO_SINIESTRO_MAP
from app.notion_sync import (
    NOTION_AVAILABLE,
    is_notion_configured,
    configurar_notion,
    desconectar_notion,
    repair_notion_databases,
    sincronizar_auditoria,
    sincronizar_todas_auditorias,
    sincronizar_todos_siniestros,
    sincronizar_tarifario_items,
    get_notion_db_urls,
)
from app.database import get_notion_url, guardar_notion_url

import dashboard.styles
from dashboard.login import gen_captcha, login

# ─── Config ───────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Facturase",
    page_icon="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzM3OGJmNCIgZD0iTTEyIDJMMyA3djVjMCA1LjU1IDMuODQgMTAuNzQgOSAxMiA1LjE2LTEuMjYgOS02LjQ1IDktMTJWN3oiLz48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTEwIDE3bC00LTQgMS40MS0xLjQxTDEwIDE0LjE3bDYuNTktNi41OUwxOCA5eiIvPjwvc3ZnPg==",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

st._config.set_option("theme.base", "light")
init_db()

# ─── Estilos ──────────────────────────────────────────────────────────────────────

st.markdown(dashboard.styles.rawStyles(), unsafe_allow_html=True)

# ─── Constantes ───────────────────────────────────────────────────────────────

TIPO_DISC_LABEL = {
    "precio_excedido":      "Precio excedido",
    "codigo_no_encontrado": "Codigo no registrado",
    "duplicado":            "Item duplicado",
    "item_incoherente":     "Incoherente con siniestro",
}
CATEGORIAS_TAR = ["insumo", "mano_obra", "servicio"]

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36">
  <path fill="#3b82f6" d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7z"/>
  <path fill="white" d="M10 17l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9z"/>
</svg>"""

# SVG icons used only inside st.markdown(unsafe_allow_html=True)
ICON = {
    "metricas":   '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#1856b4" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "auditar":    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#1856b4" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>',
    "cola":       '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#1856b4" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
    "historial":  '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#1856b4" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "siniestros": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#1856b4" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "tarifario":  '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#1856b4" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    "notion":     '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fff"><path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.906c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933zM1.936 1.035l13.31-.98c1.634-.14 2.055-.047 3.082.7l4.249 2.986c.7.513.934.653.934 1.213v16.378c0 1.026-.373 1.634-1.68 1.726l-15.458.934c-.98.047-1.448-.093-1.962-.747l-3.129-4.06c-.56-.747-.793-1.306-.793-1.96V2.667c0-.839.374-1.54 1.447-1.632z"/></svg>',
}

NAV_ITEMS = [
    ("metricas",   "Dashboard",         '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'),
    ("auditar",    "Auditar Factura",   '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>'),
    ("cola",       "Cola de revisión",  '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>'),
    ("historial",  "Historial",         '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'),
    ("siniestros", "Siniestros",        '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'),
    ("tarifario",  "Tarifario",         '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>'),
    ("notion",     "Notion Sync",       '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.906c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933z"/></svg>'),
]

# ─── Captcha ──────────────────────────────────────────────────────────────────

generar_captcha = gen_captcha

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "captcha" not in st.session_state:
    st.session_state.captcha = generar_captcha()

# ─── Session token persistence (restore login after page reload) ──────────────
_token = st.query_params.get("s", "")
if not st.session_state.logged_in and _token:
    _user = validate_session(_token)
    if _user:
        st.session_state.logged_in = True
        st.session_state.username = _user
        st.session_state["_stoken"] = _token

# ─── Login ──────────────────────────────────────────────────────────────────────

login(st, verificar_usuario, listar_usuarios_count, LOGO_SVG)

# After successful login, issue a session token and put it in URL
if st.session_state.logged_in and not st.session_state.get("_stoken"):
    _new_token = create_session(st.session_state.username)
    st.session_state["_stoken"] = _new_token
    st.query_params["s"] = _new_token
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP

if "pagina" not in st.session_state:
    st.session_state.pagina = "metricas"
if "modo_prueba" not in st.session_state:
    st.session_state.modo_prueba = True   # Activo por defecto
if "mostrar_equipo" not in st.session_state:
    st.session_state.mostrar_equipo = False

# Handle nav from HTML anchor clicks (?nav=key in URL)
_nav_qp = st.query_params.get("nav", "")
if _nav_qp and _nav_qp in {k for k, _, _ in NAV_ITEMS}:
    st.session_state.pagina = _nav_qp
    # Keep the session token when clearing nav param
    _cur_tok = st.session_state.get("_stoken", "")
    st.query_params.clear()
    if _cur_tok:
        st.query_params["s"] = _cur_tok
    st.rerun()

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.6rem 1.4rem 1.1rem 1.4rem;
                border-bottom:1px solid #162236;margin-bottom:0.15rem">
        {LOGO_SVG}
        <div style="font-size:1.25rem;font-weight:800;color:#ffffff;
                    letter-spacing:-0.03em;margin:0.45rem 0 0.05rem 0;
                    line-height:1.1">Facturase</div>
        <div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.1em;color:#253c55">Auditoria Inteligente · IA</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0.6rem 1.4rem 0.2rem 1.4rem;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#1e3550">Modulos</div>', unsafe_allow_html=True)
    
    _nav_html = '<div class="navmenu">'
    _tok = st.session_state.get("_stoken", "")
    for key, label, icon_svg in NAV_ITEMS:
        _active_cls = " nav-active" if st.session_state.pagina == key else ""
        _href = f"?nav={key}&s={_tok}" if _tok else f"?nav={key}"
        _nav_html += (
            f'<a href="{_href}" class="nav-item-link{_active_cls}">'
            f'{icon_svg}<span>{label}</span></a>'
        )
    _nav_html += '</div>'
    st.markdown(_nav_html, unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid #0f1e30;margin:0.5rem 0">', unsafe_allow_html=True)
    st.markdown('<div style="padding:0.3rem 1.4rem 0.2rem 1.4rem;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#1e3550">Configuracion</div>', unsafe_allow_html=True)

    modo_prueba = st.toggle("Modo prueba", value=st.session_state.modo_prueba,
                            help="Muestra siniestros y facturas de demo precargadas")
    st.session_state.modo_prueba = modo_prueba
    if modo_prueba:
        st.markdown('<div style="font-size:0.7rem;color:#d97706;padding:0 1.4rem 0.2rem 1.4rem">Datos de demo activos</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid #0f1e30;margin:0.5rem 0">', unsafe_allow_html=True)

    st.markdown('<div class="equipobtn">', unsafe_allow_html=True)
    if st.button("Acerca del equipo", key="nav_equipo", use_container_width=True):
        st.session_state.mostrar_equipo = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


    st.markdown(f"""
    <a href="https://github.com/tomvargasd/facturase_HACKIATHON" target="_blank"
       style="display:flex;align-items:center;gap:0.5rem;padding:0.45rem 1.4rem;
              color:#2d4d66 !important;text-decoration:none;font-size:0.78rem">
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="#2d4d66">
            <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
        </svg>
        Ver en GitHub
    </a>
    <div style="display:flex;align-items:center;gap:0.55rem;padding:0.35rem 1.4rem 0.9rem 1.4rem;
                border-top:1px solid #0f1e30;margin-top:0.4rem">
        <div style="width:27px;height:27px;border-radius:50%;background:#1856b4;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.68rem;font-weight:700;color:#fff">
            {st.session_state.username[0].upper() if st.session_state.username else 'U'}
        </div>
        <div>
            <div style="font-size:0.78rem;color:#8fadc8;font-weight:600">{st.session_state.username}</div>
            <div style="font-size:0.63rem;color:#253c55">v1.0.0 · Gemini 2.5 Flash</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar sesion", key="logout", use_container_width=True):
        _tok = st.session_state.get("_stoken", "")
        if _tok:
            delete_session(_tok)
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state["_stoken"] = ""
        st.query_params.clear()
        st.rerun()

# ─── Modal equipo ─────────────────────────────────────────────────────────────

@st.dialog("HackIAThon — Equipo participante")
def modal_equipo():
    st.markdown(f"""
    <div style="text-align:center;padding:0.4rem 0 1.1rem 0">
        {LOGO_SVG}
        <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-top:0.4rem">HackIAThon 2026</div>
        <div style="font-size:0.8rem;color:#64748b">Solucion desarrollada como prueba oficial del HackIAThon.</div>
    </div>
    <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 0 0.85rem 0">
    <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                letter-spacing:0.1em;color:#94a3b8;margin-bottom:0.55rem">Equipo</div>
    """, unsafe_allow_html=True)

    for rol, nombre, correo in [
        ("Lider",   "Tomas Vargas Drouet",  "tomvargasd@gmail.com"),
        ("Miembro", "Alexa Granizo Ramirez", "alexagranizo06@gmail.com"),
        ("Miembro", "Angie Granizo Ramirez", "angiegranizor@gmail.com"),
    ]:
        badge = '<span style="background:#dcfce7;color:#166534;font-size:0.58rem;font-weight:700;padding:1px 6px;border-radius:9999px;margin-left:5px;vertical-align:middle">LIDER</span>' if rol == "Lider" else ""
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0.7rem;
                    background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.4rem">
            <div style="width:32px;height:32px;border-radius:50%;background:#dbeafe;flex-shrink:0;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:700;color:#1856b4;font-size:0.82rem">{nombre[0]}</div>
            <div>
                <div style="font-weight:600;color:#0f172a;font-size:0.845rem">{nombre}{badge}</div>
                <a href="mailto:{correo}" style="font-size:0.75rem;color:#1856b4;text-decoration:none">{correo}</a>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:0.75rem;padding:0.65rem 0.85rem;background:#f0fdf4;
                border:1px solid #bbf7d0;border-radius:10px;
                display:flex;align-items:center;gap:0.6rem">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#25d366">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
            <path d="M12 0C5.373 0 0 5.373 0 12c0 2.124.558 4.118 1.528 5.845L0 24l6.335-1.507A11.945 11.945 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.898 0-3.664-.53-5.166-1.44l-.371-.22-3.762.895.942-3.655-.242-.38A9.945 9.945 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>
        </svg>
        <div>
            <div style="font-size:0.7rem;font-weight:600;color:#166534">Contacto del equipo</div>
            <a href="https://wa.me/593960745756" target="_blank"
               style="font-size:0.82rem;color:#25d366;font-weight:700;text-decoration:none">
                +593 960 745 756 (WhatsApp)
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.mostrar_equipo:
    modal_equipo()
    st.session_state.mostrar_equipo = False

# ─── Helpers UI ───────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str, key: str) -> None:
    st.markdown(f"""
    <div class="page-header">
        {ICON.get(key, '')}
        <div><h2>{title}</h2><p>{subtitle}</p></div>
    </div>""", unsafe_allow_html=True)


def badge_resultado(resultado: str) -> str:
    signs = {"APROBADA": "&#10003;", "OBSERVADA": "!", "RECHAZADA": "&#10005;"}
    return f'<span class="badge badge-{resultado}">{signs.get(resultado,"")} {resultado}</span>'


def render_dictamen(dictamen: dict) -> None:
    resultado = dictamen["resultado"]
    st.markdown(f"""
    <div class="dictamen-card">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem">
            <div>
                <div style="font-size:0.7rem;color:#64748b;font-weight:600;
                            text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.2rem">Dictamen</div>
                {badge_resultado(resultado)}
            </div>
            <div style="text-align:right;font-size:0.77rem;color:#94a3b8">
                Factura: <strong style="color:#0f172a">{dictamen.get('factura_id','—')}</strong><br>
                Siniestro: <strong style="color:#0f172a">{dictamen.get('siniestro_id','—')}</strong>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Confianza IA",     f"{dictamen['confianza']:.0%}")
    c2.metric("Items aprobados",  dictamen["items_aprobados"])
    c3.metric("Items observados", dictamen["items_observados"])
    c4.metric("Discrepancias $",  f"${dictamen['monto_discrepancias']:,.2f}")

    if dictamen["requiere_revision_humana"]:
        st.markdown('<div class="alerta-revision"><strong>Requiere revision humana</strong> — Revisar con ajustador antes de proceder.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alerta-ok"><strong>Sin revision adicional</strong> — Puede procesarse automaticamente.</div>', unsafe_allow_html=True)

    with st.expander("Razonamiento del agente", expanded=True):
        st.write(dictamen["razonamiento"])
        st.info(f"**Recomendacion:** {dictamen['recomendacion']}")

    discs = dictamen.get("discrepancias", [])
    if discs:
        st.subheader("Discrepancias detectadas")
        rows = []
        for d in discs:
            tipo = TIPO_DISC_LABEL.get(d.get("tipo",""), d.get("tipo",""))
            item = d.get("item") or d.get("descripcion") or d.get("codigo","")
            if d.get("tipo") == "precio_excedido":
                det = f"Cobrado ${d['cobrado']:,.2f} / Max ${d['tarifario_max']:,.2f} / Dif ${d['diferencia']:,.2f}"
            elif d.get("tipo") == "duplicado":
                det = f"Aparece {d['ocurrencias']} veces"
            elif d.get("tipo") == "codigo_no_encontrado":
                det = f"Codigo: {d.get('codigo','')}"
            else:
                det = d.get("razon","")
            rows.append({"Tipo": tipo, "Item": item, "Detalle": det})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        tipo_counts = pd.Series([d.get("tipo","") for d in discs]).value_counts()
        tipo_counts.index = [TIPO_DISC_LABEL.get(t, t) for t in tipo_counts.index]
        fig = px.pie(values=tipo_counts.values, names=tipo_counts.index,
                     color_discrete_sequence=["#ef4444","#f59e0b","#3b82f6","#a855f7"], hole=0.45)
        fig.update_layout(height=240, margin=dict(t=10,b=10,l=10,r=10),
                          legend=dict(orientation="h", y=-0.2))
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="alerta-ok">Sin discrepancias detectadas.</div>', unsafe_allow_html=True)

    with st.expander("JSON completo del dictamen"):
        st.json(dictamen)

    # ─── Abrir en Notion ─────────────────────────────────────────────────────
    audit_id = dictamen.get("id")
    notion_url = get_notion_url("auditoria", str(audit_id)) if audit_id else None

    if is_notion_configured():
        nc1, nc2 = st.columns([1, 3])
        with nc1:
            if notion_url:
                st.markdown(
                    f'<a href="{notion_url}" target="_blank" style="display:inline-flex;'
                    'align-items:center;gap:0.4rem;background:#000;color:#fff;padding:0.45rem 1rem;'
                    'border-radius:8px;font-size:0.82rem;font-weight:600;text-decoration:none">'
                    '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="#fff">'
                    '<path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.906c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933z"/></svg>'
                    ' Abrir en Notion</a>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button("Subir a Notion", key=f"notion_upload_{audit_id or 'last'}"):
                    with st.spinner("Sincronizando con Notion..."):
                        try:
                            url = sincronizar_auditoria(dictamen, audit_db_id=audit_id)
                            if url:
                                st.success("Sincronizado.")
                                st.rerun()
                            else:
                                st.error("No se pudo sincronizar. Verifica la configuracion de Notion.")
                        except Exception as exc:
                            st.error(f"Error: {exc}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGINAS
# ══════════════════════════════════════════════════════════════════════════════

pagina = st.session_state.pagina

# ─── Dashboard (Metricas) ─────────────────────────────────────────────────────
if pagina == "metricas":
    page_header("Dashboard", "Indicadores de desempeno y acciones rapidas", "metricas")

    st.markdown("#### Acciones rapidas")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown("""<div class="quick-card">
            <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#1856b4" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
            <div style="font-weight:600;color:#0f172a;margin-top:0.45rem;font-size:0.88rem">Nueva auditoría</div>
            <div style="font-size:0.75rem;color:#64748b">Analiza una factura individualmente</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-nueva">', unsafe_allow_html=True)
        if st.button("Ir a Auditar", key="qa_auditar", use_container_width=True):
            st.session_state.pagina = "auditar"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with qa2:
        st.markdown("""<div class="quick-card">
            <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
            <div style="font-weight:600;color:#0f172a;margin-top:0.45rem;font-size:0.88rem">Agregar a cola</div>
            <div style="font-size:0.75rem;color:#64748b">Acumula casos para procesar en lote</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-cola">', unsafe_allow_html=True)
        if st.button("Ir a Cola", key="qa_cola", use_container_width=True):
            st.session_state.pagina = "cola"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with qa3:
        st.markdown("""<div class="quick-card">
            <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <div style="font-weight:600;color:#0f172a;margin-top:0.45rem;font-size:0.88rem">Nuevo siniestro</div>
            <div style="font-size:0.75rem;color:#64748b">Registra un expediente nuevo</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="qa-btn-siniestro">', unsafe_allow_html=True)
        if st.button("Ir a Siniestros", key="qa_siniestros", use_container_width=True):
            st.session_state.pagina = "siniestros"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    auditorias = listar_auditorias(500)
    if not auditorias:
        st.info("Aun no se han realizado auditorias.")
    else:
        total      = len(auditorias)
        aprobadas  = sum(1 for a in auditorias if a["resultado"] == "APROBADA")
        observadas = sum(1 for a in auditorias if a["resultado"] == "OBSERVADA")
        rechazadas = sum(1 for a in auditorias if a["resultado"] == "RECHAZADA")
        ahorro     = sum(a["monto_discrepancias"] for a in auditorias)
        rev_hum    = sum(1 for a in auditorias if a["requiere_revision_humana"])

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total auditadas", total)
        c2.metric("Aprobadas",  aprobadas,  f"{aprobadas/total:.0%}")
        c3.metric("Observadas", observadas, f"{observadas/total:.0%}")
        c4.metric("Rechazadas", rechazadas, f"{rechazadas/total:.0%}")
        c5.metric("Rev. humana", rev_hum)
        c6.metric("Ahorro detectado", f"${ahorro:,.0f}")

        cl, cr = st.columns(2)
        with cl:
            fig_pie = px.pie(
                values=[aprobadas, observadas, rechazadas],
                names=["Aprobada","Observada","Rechazada"],
                color_discrete_map={"Aprobada":"#22c55e","Observada":"#f59e0b","Rechazada":"#ef4444"},
                hole=0.45, title="Distribucion de resultados",
            )
            fig_pie.update_layout(height=280, margin=dict(t=40,b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        with cr:
            df_conf = pd.DataFrame([{"Resultado": a["resultado"], "Confianza": a["confianza"]} for a in auditorias])
            fig_box = px.box(df_conf, x="Resultado", y="Confianza", color="Resultado",
                             color_discrete_map={"APROBADA":"#22c55e","OBSERVADA":"#f59e0b","RECHAZADA":"#ef4444"},
                             title="Confianza por resultado")
            fig_box.update_layout(height=280, margin=dict(t=40,b=10), showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

        tipo_counts: dict = {}
        for a in auditorias:
            for d in a.get("discrepancias", []):
                t = TIPO_DISC_LABEL.get(d.get("tipo",""), d.get("tipo",""))
                tipo_counts[t] = tipo_counts.get(t, 0) + 1
        if tipo_counts:
            st.subheader("Tipos de discrepancia mas frecuentes")
            fig_bar = px.bar(x=list(tipo_counts.keys()), y=list(tipo_counts.values()),
                             labels={"x":"Tipo","y":"Frecuencia"}, color=list(tipo_counts.values()),
                             color_continuous_scale=["#fef9c3","#f97316","#ef4444"])
            fig_bar.update_layout(height=260, coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)

# ─── Auditar ──────────────────────────────────────────────────────────────────
elif pagina == "auditar":
    page_header("Auditar Factura", "Analiza una factura contra el tarifario y el siniestro", "auditar")

    siniestros = listar_siniestros()
    siniestros_visibles = siniestros if st.session_state.modo_prueba else (
        [s for s in siniestros if not s["id"].startswith("SIN-2025")] or siniestros
    )
    if not siniestros_visibles:
        st.warning("No hay siniestros disponibles. Activa el Modo prueba o registra uno.")
        st.stop()

    st.markdown("#### 1. Expediente del siniestro")
    labels = {s["id"]: f"{s['id']} — {s['tipo_accidente']} · {s['vehiculo'][:45]}" for s in siniestros_visibles}
    siniestro_id = st.selectbox("Expediente", options=list(labels.keys()),
                                format_func=lambda x: labels[x], label_visibility="collapsed")
    siniestro = obtener_siniestro(siniestro_id)
    if siniestro:
        with st.expander("Ver detalle del expediente"):
            ca, cb = st.columns(2)
            ca.markdown(f"**Vehiculo:** {siniestro['vehiculo']}")
            ca.markdown(f"**Tipo:** {siniestro['tipo_accidente']}")
            ca.markdown(f"**Fecha:** {siniestro['fecha_accidente']}")
            cb.markdown(f"**Poliza:** {siniestro['poliza']}")
            cb.markdown(f"**Partes afectadas:** {', '.join(siniestro['partes_afectadas'])}")
            st.markdown(f"**Descripcion:** {siniestro['descripcion']}")

    st.markdown("#### 2. Factura a auditar")
    tab_pdf, tab_demo = st.tabs(["Subir PDF", "Factura de demostracion"])
    factura_json = None
    pdf_bytes = None

    with tab_pdf:
        uploaded = st.file_uploader("Archivo PDF", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            pdf_bytes = uploaded.read()
            st.success(f"Archivo listo: {uploaded.name}  ({len(pdf_bytes):,} bytes)")

    with tab_demo:
        if not st.session_state.modo_prueba:
            st.info("Activa el Modo prueba en el sidebar para ver las facturas de demostracion.")
        else:
            demo_key = st.selectbox(
                "Factura demo", options=list(FACTURAS_DEMO.keys()),
                format_func=lambda k: f"{k} — {FACTURAS_DEMO[k]['numero_factura']} ({FACTURAS_DEMO[k]['taller']})",
                label_visibility="collapsed",
            )
            if demo_key in DEMO_SINIESTRO_MAP and DEMO_SINIESTRO_MAP[demo_key] != siniestro_id:
                st.warning(f"Esta demo corresponde al siniestro {DEMO_SINIESTRO_MAP[demo_key]}.")
            fp = FACTURAS_DEMO[demo_key]
            with st.expander(f"Vista previa: {fp['numero_factura']}"):
                df_prev = pd.DataFrame(fp["items"])
                df_prev.columns = ["Codigo","Descripcion","Cantidad","P. Unitario","Total","Tipo"]
                df_prev["P. Unitario"] = df_prev["P. Unitario"].apply(lambda x: f"${x:,.2f}")
                df_prev["Total"]       = df_prev["Total"].apply(lambda x: f"${x:,.2f}")
                st.dataframe(df_prev, use_container_width=True, hide_index=True)
                st.metric("Total factura", f"${fp['total_factura']:,.2f}")
            factura_json = FACTURAS_DEMO[demo_key]

    st.markdown("#### 3. Accion")
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        if st.button("Ejecutar auditoria ahora", type="primary", use_container_width=True):
            if factura_json is None and pdf_bytes is None:
                st.error("Selecciona una factura demo o sube un PDF.")
            else:
                with st.spinner("Analizando con IA..."):
                    try:
                        dictamen = auditar_factura(siniestro, pdf_bytes=pdf_bytes, factura_json=factura_json)
                        st.session_state["ultimo_dictamen"] = dictamen
                        # Auto-sync to Notion if configured
                        if is_notion_configured():
                            try:
                                notion_url = sincronizar_auditoria(
                                    dictamen,
                                    audit_db_id=dictamen.get("id"),
                                )
                                if notion_url:
                                    st.session_state["ultimo_dictamen_notion_url"] = notion_url
                            except Exception:
                                pass  # Notion sync failure is non-blocking
                    except Exception as e:
                        st.error(f"Error durante la auditoria: {e}")
                        st.exception(e)
    with btn_c2:
        nombre_cola = st.text_input("Nombre para la cola (opcional)", placeholder="Factura-001",
                                    label_visibility="collapsed")
        if st.button("Agregar a cola de procesamiento", use_container_width=True):
            if factura_json is None and pdf_bytes is None:
                st.error("Selecciona una factura demo o sube un PDF.")
            elif factura_json is None:
                st.warning("La cola actualmente soporta facturas en formato JSON/demo.")
            else:
                nombre = nombre_cola.strip() or factura_json.get("numero_factura", "sin-nombre")
                agregar_a_cola(siniestro_id, nombre, factura_json)
                st.success(f"Agregado a cola: **{nombre}**")

    if "ultimo_dictamen" in st.session_state:
        st.divider()
        render_dictamen(st.session_state["ultimo_dictamen"])

# ─── Cola de Procesamiento ────────────────────────────────────────────────────
elif pagina == "cola":
    page_header("Cola de Procesamiento", "Procesa en lote multiples siniestros con sus facturas", "cola")

    tab_ver, tab_agregar = st.tabs(["Ver cola", "Agregar a cola"])

    with tab_ver:
        cola = listar_cola()
        pendientes  = [i for i in cola if i["estado"] == "pendiente"]
        completados = [i for i in cola if i["estado"] == "completado"]
        con_error   = [i for i in cola if i["estado"] == "error"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total en cola", len(cola))
        m2.metric("Pendientes",   len(pendientes))
        m3.metric("Completados",  len(completados))
        m4.metric("Con error",    len(con_error))

        if not cola:
            st.info("La cola esta vacia. Agrega casos desde 'Auditar' o desde la pestana 'Agregar a cola'.")
        else:
            estado_color = {
                "pendiente":   "#3b82f6",
                "procesando":  "#f59e0b",
                "completado":  "#22c55e",
                "error":       "#ef4444",
            }
            for item in cola:
                col_info, col_del = st.columns([9, 1])
                with col_info:
                    c = estado_color.get(item["estado"], "#94a3b8")
                    err_html = f'<div style="font-size:0.71rem;color:#ef4444;margin-top:2px">{item["error_msg"]}</div>' if item.get("error_msg") else ""
                    st.markdown(f"""
                    <div class="queue-item">
                        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.4rem">
                            <div>
                                <span style="font-weight:600;color:#0f172a;font-size:0.865rem">{item['nombre_factura']}</span>
                                <span style="font-size:0.75rem;color:#64748b;margin-left:0.5rem">
                                    Siniestro: {item['siniestro_id']}</span>
                                {err_html}
                            </div>
                            <span style="background:{c}18;color:{c};font-size:0.7rem;font-weight:700;
                                         padding:0.18rem 0.6rem;border-radius:9999px;border:1px solid {c}40">
                                {item['estado'].upper()}
                            </span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with col_del:
                    if st.button("x", key=f"del_cola_{item['id']}", help="Eliminar"):
                        eliminar_de_cola(item["id"])
                        st.rerun()

        st.markdown("---")
        c_proc, c_clean = st.columns(2)
        with c_proc:
            if st.button("Procesar todos los pendientes", type="primary",
                         use_container_width=True, disabled=len(pendientes) == 0):
                pb = st.progress(0, text="Iniciando...")
                resultados = []
                for i, item in enumerate(pendientes):
                    pb.progress(i / len(pendientes), text=f"Procesando {item['nombre_factura']} ({i+1}/{len(pendientes)})")
                    actualizar_estado_cola(item["id"], "procesando")
                    try:
                        s = obtener_siniestro(item["siniestro_id"])
                        f = json.loads(item["factura_json"])
                        d = auditar_factura(s, factura_json=f)
                        actualizar_estado_cola(item["id"], "completado")
                        resultados.append((item["nombre_factura"], True, d["resultado"]))
                    except Exception as e:
                        actualizar_estado_cola(item["id"], "error", str(e)[:200])
                        resultados.append((item["nombre_factura"], False, str(e)[:80]))
                pb.progress(1.0, text="Completado")
                for nombre, ok, detalle in resultados:
                    cls = "alerta-ok" if ok else "alerta-revision"
                    st.markdown(f'<div class="{cls}"><strong>{nombre}</strong> — {detalle}</div>', unsafe_allow_html=True)
                st.rerun()
        with c_clean:
            if st.button("Limpiar completados / errores", use_container_width=True,
                         disabled=(len(completados) + len(con_error)) == 0):
                limpiar_cola_completados()
                st.success("Cola limpiada.")
                st.rerun()

    with tab_agregar:
        st.markdown("##### Agregar caso a la cola")
        siniestros = listar_siniestros()
        siniestros_vis = siniestros if st.session_state.modo_prueba else (
            [s for s in siniestros if not s["id"].startswith("SIN-2025")] or siniestros
        )
        with st.form("form_agregar_cola", clear_on_submit=True):
            c1, c2 = st.columns(2)
            labels_c = {s["id"]: f"{s['id']} — {s['vehiculo'][:38]}" for s in siniestros_vis}
            sel_sin = c1.selectbox("Siniestro *", options=list(labels_c.keys()),
                                   format_func=lambda x: labels_c[x])
            if st.session_state.modo_prueba and FACTURAS_DEMO:
                demo_sel = c2.selectbox("Factura demo *", options=list(FACTURAS_DEMO.keys()),
                                        format_func=lambda k: f"{k} — {FACTURAS_DEMO[k]['numero_factura']}")
            else:
                demo_sel = None
                c2.info("Activa Modo prueba para seleccionar facturas demo.")
            nombre_item = st.text_input("Nombre identificador *", placeholder="Caso-001")
            sub_cola = st.form_submit_button("Agregar a cola", type="primary", use_container_width=True)
            if sub_cola:
                if not nombre_item.strip():
                    st.error("El nombre identificador es obligatorio.")
                elif demo_sel is None:
                    st.error("Activa el Modo prueba para seleccionar una factura demo.")
                else:
                    agregar_a_cola(sel_sin, nombre_item.strip(), FACTURAS_DEMO[demo_sel])
                    st.success(f"Agregado: **{nombre_item.strip()}**")
                    st.rerun()

# ─── Historial ────────────────────────────────────────────────────────────────
elif pagina == "historial":
    page_header("Historial de Auditorias", "Registro completo de todas las auditorias ejecutadas", "historial")

    auditorias = listar_auditorias()
    if not auditorias:
        st.info("Aun no se han realizado auditorias.")
    else:
        rows = [{
            "#": a["id"], "Factura": a["factura_id"], "Siniestro": a["siniestro_id"],
            "Resultado": a["resultado"], "Confianza": f"{a['confianza']:.0%}",
            "Disc.": a["items_observados"], "Total": f"${a['monto_total_factura']:,.2f}",
            "Dif. $": f"${a['monto_discrepancias']:,.2f}",
            "Rev. humana": "Si" if a["requiere_revision_humana"] else "No",
            "Fecha": a["timestamp"][:19].replace("T", " "),
        } for a in auditorias]
        df = pd.DataFrame(rows)

        def _color(val: str) -> str:
            m = {
                "APROBADA": "background:#dcfce7;color:#166534",
                "OBSERVADA": "background:#fef9c3;color:#854d0e",
                "RECHAZADA": "background:#fee2e2;color:#991b1b",
            }
            return m.get(val, "")

        st.dataframe(df.style.map(_color, subset=["Resultado"]),
                     use_container_width=True, hide_index=True)

        sel_id = st.selectbox(
            "Ver detalle", [a["id"] for a in auditorias],
            format_func=lambda x: f"#{x} — {next(a['factura_id'] for a in auditorias if a['id']==x)}"
        )
        if sel_id:
            render_dictamen(next(a for a in auditorias if a["id"] == sel_id))

# ─── Siniestros ───────────────────────────────────────────────────────────────
elif pagina == "siniestros":
    page_header("Gestion de Siniestros", "Registra, consulta y administra expedientes", "siniestros")

    tab_lista, tab_nuevo = st.tabs(["Lista de siniestros", "Registrar nuevo"])

    with tab_lista:
        siniestros = listar_siniestros()
        visibles = siniestros if st.session_state.modo_prueba else (
            [s for s in siniestros if not s["id"].startswith("SIN-2025")] or []
        )
        if not visibles:
            st.info("No hay siniestros. Usa 'Registrar nuevo' o activa el Modo prueba.")
        else:
            rows = [{"ID": s["id"], "Tipo": s["tipo_accidente"], "Vehiculo": s["vehiculo"][:50],
                     "Poliza": s["poliza"], "Fecha": s["fecha_accidente"],
                     "Partes afectadas": ", ".join(s["partes_afectadas"])} for s in visibles]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            with st.expander("Ver detalle de un siniestro"):
                sid = st.selectbox("Seleccionar", [s["id"] for s in visibles], key="sel_sin_detail")
                s = obtener_siniestro(sid)
                if s:
                    ca, cb = st.columns(2)
                    ca.markdown(f"**ID:** {s['id']}")
                    ca.markdown(f"**Tipo:** {s['tipo_accidente']}")
                    ca.markdown(f"**Fecha:** {s['fecha_accidente']}")
                    cb.markdown(f"**Vehiculo:** {s['vehiculo']}")
                    cb.markdown(f"**Poliza:** {s['poliza']}")
                    st.markdown(f"**Partes afectadas:** {', '.join(s['partes_afectadas'])}")
                    st.markdown(f"**Descripcion:** {s['descripcion']}")

            with st.expander("Eliminar siniestro"):
                sid_del = st.selectbox("Siniestro a eliminar", [s["id"] for s in visibles], key="sel_sin_del")
                if st.button("Confirmar eliminacion", type="primary", key="btn_del_sin"):
                    eliminar_siniestro(sid_del)
                    st.success(f"Siniestro {sid_del} eliminado.")
                    st.rerun()

    with tab_nuevo:
        with st.form("form_nuevo_siniestro", clear_on_submit=True):
            st.markdown("##### Datos del expediente")
            c1, c2 = st.columns(2)
            nuevo_id     = c1.text_input("ID del siniestro *", placeholder="SIN-2026-001")
            nueva_poliza = c2.text_input("Numero de poliza *", placeholder="POL-MX-00012345")
            c3, c4 = st.columns(2)
            tipo_acc  = c3.selectbox("Tipo de accidente *", [
                "Colision frontal","Colision trasera","Impacto lateral",
                "Volcadura","Robo parcial","Granizo","Inundacion","Otro"])
            fecha_acc = c4.date_input("Fecha del accidente *", value=date.today())
            vehiculo_str    = st.text_input("Descripcion del vehiculo *", placeholder="Toyota Corolla 2023 LE, blanco")
            partes_str      = st.text_input("Partes afectadas (separadas por coma) *", placeholder="cofre, defensa, faro")
            descripcion_str = st.text_area("Descripcion del accidente", height=88)
            submitted = st.form_submit_button("Registrar siniestro", type="primary", use_container_width=True)
            if submitted:
                errs = []
                if not nuevo_id.strip():     errs.append("El ID es obligatorio.")
                if not nueva_poliza.strip(): errs.append("La poliza es obligatoria.")
                if not vehiculo_str.strip(): errs.append("El vehiculo es obligatorio.")
                if not partes_str.strip():   errs.append("Las partes afectadas son obligatorias.")
                if obtener_siniestro(nuevo_id.strip()):
                    errs.append(f"Ya existe el siniestro '{nuevo_id.strip()}'.")
                if errs:
                    for e in errs: st.error(e)
                else:
                    crear_siniestro({
                        "id": nuevo_id.strip(), "tipo_accidente": tipo_acc,
                        "partes_afectadas": [p.strip() for p in partes_str.split(",") if p.strip()],
                        "vehiculo": vehiculo_str.strip(), "poliza": nueva_poliza.strip(),
                        "fecha_accidente": str(fecha_acc), "descripcion": descripcion_str.strip(),
                    })
                    st.success(f"Siniestro **{nuevo_id.strip()}** registrado.")
                    st.rerun()

# ─── Tarifario ────────────────────────────────────────────────────────────────
elif pagina == "tarifario":
    page_header("Gestion del Tarifario", "Administra los precios de referencia para auditoria", "tarifario")

    tab_ver, tab_nuevo, tab_eliminar = st.tabs(["Lista de precios", "Agregar item", "Eliminar item"])

    with tab_ver:
        items = listar_tarifario()
        if not items:
            st.info("El tarifario esta vacio.")
        else:
            cat_filter = st.selectbox("Filtrar por categoria", ["Todas"] + CATEGORIAS_TAR, key="tar_filter")
            df_tar = pd.DataFrame(items)
            if cat_filter != "Todas":
                df_tar = df_tar[df_tar["categoria"] == cat_filter]
            df_tar = df_tar.rename(columns={
                "codigo":"Codigo","descripcion":"Descripcion",
                "precio_min":"P. Min","precio_max":"P. Max",
                "unidad":"Unidad","categoria":"Categoria",
                "vigente_desde":"Desde","vigente_hasta":"Hasta",
            })
            df_tar["P. Min"] = df_tar["P. Min"].apply(lambda x: f"${x:,.2f}")
            df_tar["P. Max"] = df_tar["P. Max"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_tar, use_container_width=True, hide_index=True)
            st.caption(f"{len(df_tar)} items mostrados")

    with tab_nuevo:
        with st.form("form_nuevo_tar", clear_on_submit=True):
            st.markdown("##### Nuevo item en el tarifario")
            c1, c2 = st.columns(2)
            tar_cod  = c1.text_input("Codigo *", placeholder="HOJ-007")
            tar_desc = c2.text_input("Descripcion *", placeholder="Tapa de cajuela")
            c3, c4, c5 = st.columns(3)
            tar_pmin = c3.number_input("Precio minimo *", min_value=0.0, step=50.0, format="%.2f")
            tar_pmax = c4.number_input("Precio maximo *", min_value=0.0, step=50.0, format="%.2f")
            tar_uni  = c5.text_input("Unidad", value="pieza")
            c6, c7, c8 = st.columns(3)
            tar_cat   = c6.selectbox("Categoria *", CATEGORIAS_TAR)
            tar_desde = c7.date_input("Vigente desde", value=date.today())
            tar_hasta = c8.date_input("Vigente hasta", value=date(2026, 12, 31))
            sub_tar = st.form_submit_button("Agregar al tarifario", type="primary", use_container_width=True)
            if sub_tar:
                errs = []
                if not tar_cod.strip():  errs.append("El codigo es obligatorio.")
                if not tar_desc.strip(): errs.append("La descripcion es obligatoria.")
                if tar_pmax <= 0:        errs.append("El precio maximo debe ser mayor a 0.")
                if tar_pmax < tar_pmin:  errs.append("El precio maximo no puede ser menor al minimo.")
                if errs:
                    for e in errs: st.error(e)
                else:
                    agregar_item_tarifario({
                        "codigo": tar_cod.strip().upper(), "descripcion": tar_desc.strip(),
                        "precio_min": tar_pmin, "precio_max": tar_pmax,
                        "unidad": tar_uni.strip() or "pieza", "categoria": tar_cat,
                        "vigente_desde": str(tar_desde), "vigente_hasta": str(tar_hasta),
                    })
                    st.success(f"Item **{tar_cod.strip().upper()}** agregado.")
                    st.rerun()

    with tab_eliminar:
        items = listar_tarifario()
        if not items:
            st.info("El tarifario esta vacio.")
        else:
            cod_del = st.selectbox(
                "Item a eliminar", [i["codigo"] for i in items],
                format_func=lambda c: f"{c} — {next(i['descripcion'] for i in items if i['codigo']==c)}",
            )
            st.warning(f"Se eliminara permanentemente **{cod_del}** del tarifario.")
            if st.button("Confirmar eliminacion", type="primary", key="btn_del_tar"):
                eliminar_item_tarifario(cod_del)
                st.success(f"Item {cod_del} eliminado.")
                st.rerun()

# ─── Notion Sync ──────────────────────────────────────────────────────────────
elif pagina == "notion":
    page_header("Notion Sync", "Sincroniza tus datos con Notion (solo lectura visual)", "notion")

    if not NOTION_AVAILABLE:
        st.error(
            "La librería **notion-client** no está instalada. "
            "Ejecuta `pip install notion-client` y reinicia la app."
        )
        st.stop()

    configured = is_notion_configured()

    # ── Sin conexión: setup flow ──────────────────────────────────────────────
    if not configured:
        st.markdown("""
        <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;
                    padding:1.4rem 1.6rem;margin-bottom:1.2rem">
            <div style="font-size:1rem;font-weight:700;color:#0c4a6e;margin-bottom:0.4rem">
                Conectar con Notion
            </div>
            <p style="font-size:0.85rem;color:#0369a1;margin:0">
                Facturase creará automáticamente tres bases de datos en la página de Notion
                que elijas: <strong>Auditorias</strong>, <strong>Siniestros</strong> y
                <strong>Tarifario</strong>. Los datos se sincronizan desde la app; la vista
                en Notion es de solo lectura.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Pasos para conectar")
        st.markdown("""
        1. Abre [notion.so/my-integrations](https://www.notion.so/my-integrations) y crea una integración (tipo **Internal**).  
           Copia el **Token** (empieza con `secret_...`).
        2. En Notion, abre la página donde quieres crear las bases de datos.  
           Haz clic en **···** → **Add connections** → selecciona tu integración.
        3. Copia el **ID de la página** desde la URL:  
           `notion.so/Mi-pagina-`**`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`**`?v=...`  
           (son 32 caracteres hexadecimales, pueden tener guiones).
        4. Pega los datos abajo y haz clic en **Conectar y crear bases de datos**.
        """)

        with st.form("form_notion_setup"):
            notion_token = st.text_input(
                "Token de integración *",
                type="password",
                placeholder="secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            )
            parent_page_id = st.text_input(
                "ID de la página padre *",
                placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            )
            submitted = st.form_submit_button(
                "Conectar y crear bases de datos", type="primary", use_container_width=True
            )
            if submitted:
                if not notion_token.strip() or not parent_page_id.strip():
                    st.error("Ambos campos son obligatorios.")
                else:
                    with st.spinner("Creando bases de datos en Notion..."):
                        result = configurar_notion(
                            notion_token.strip(),
                            parent_page_id.strip().replace("-", ""),
                        )
                    if result["ok"]:
                        st.success("¡Conexión establecida! Las bases de datos fueron creadas en Notion.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error al conectar: {result['error']}")

    # ── Con conexión: panel de sincronización ─────────────────────────────────
    else:
        db_urls = get_notion_db_urls()

        st.markdown("""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;
                    padding:1rem 1.4rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:0.6rem">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#16a34a">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span style="font-size:0.9rem;font-weight:600;color:#15803d">Notion conectado y activo</span>
        </div>
        """, unsafe_allow_html=True)

        # DB links
        link_cols = st.columns(3)
        for col, (label, url_key) in zip(
            link_cols,
            [("Auditorias", "auditorias"), ("Siniestros", "siniestros"), ("Tarifario", "tarifario")],
        ):
            url = db_urls.get(url_key, "")
            with col:
                if url:
                    st.markdown(
                        f'<a href="{url}" target="_blank" style="display:flex;align-items:center;'
                        'gap:0.4rem;background:#000;color:#fff;padding:0.5rem 0.8rem;'
                        'border-radius:8px;font-size:0.8rem;font-weight:600;text-decoration:none;'
                        'justify-content:center">'
                        '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="#fff">'
                        '<path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.906c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933z"/></svg>'
                        f' Ver {label} en Notion</a>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f'<div style="color:#94a3b8;font-size:0.8rem">{label}: sin URL</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Sincronización manual")
        st.info(
            "Las auditorias se sincronizan automáticamente al ejecutar un análisis. "
            "Usa los botones de abajo para sincronizar datos históricos o hacer una "
            "sincronización completa."
        )

        sc1, sc2, sc3 = st.columns(3)

        with sc1:
            st.markdown("**Auditorias**")
            if st.button("Sincronizar todas las auditorias", use_container_width=True):
                auditorias = listar_auditorias(500)
                if not auditorias:
                    st.warning("No hay auditorias para sincronizar.")
                else:
                    with st.spinner(f"Sincronizando {len(auditorias)} auditorias..."):
                        res = sincronizar_todas_auditorias(auditorias)
                    st.success(f"Listo: {res['ok']} sincronizadas, {res['errores']} errores.")

        with sc2:
            st.markdown("**Siniestros**")
            if st.button("Sincronizar todos los siniestros", use_container_width=True):
                siniestros_all = listar_siniestros()
                if not siniestros_all:
                    st.warning("No hay siniestros para sincronizar.")
                else:
                    with st.spinner(f"Sincronizando {len(siniestros_all)} siniestros..."):
                        res = sincronizar_todos_siniestros(siniestros_all)
                    st.success(f"Listo: {res['ok']} sincronizados, {res['errores']} errores.")

        with sc3:
            st.markdown("**Tarifario**")
            if st.button("Sincronizar tarifario completo", use_container_width=True):
                items_all = listar_tarifario()
                if not items_all:
                    st.warning("El tarifario está vacío.")
                else:
                    with st.spinner(f"Sincronizando {len(items_all)} items..."):
                        res = sincronizar_tarifario_items(items_all)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"Listo: {res['ok']} sincronizados, {res['errores']} errores.")

        st.divider()
        st.markdown("#### 🔧 Reparar bases de datos")
        st.info(
            "Si la sincronización falla con errores de 'propiedad no existe', usa este botón "
            "para reconstruir las columnas en las tres bases de datos de Notion."
        )
        if st.button("Reparar columnas de Notion", use_container_width=True):
            with st.spinner("Reparando bases de datos..."):
                res_rep = repair_notion_databases()
            if res_rep["ok"]:
                st.success("✅ Columnas reparadas correctamente. Intenta sincronizar de nuevo.")
            else:
                st.error(f"Error al reparar: {res_rep['error']}")

        st.divider()
        st.markdown("#### Desconectar Notion")
        st.warning(
            "Esto eliminará la configuración de Notion de esta app. "
            "Los datos en Notion **no** serán borrados."
        )
        if st.button("Desconectar Notion", type="secondary"):
            desconectar_notion()
            st.success("Notion desconectado.")
            st.rerun()

