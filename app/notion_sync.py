from __future__ import annotations
"""
Integración con Notion API.
Sincroniza datos de Facturase (auditorias, siniestros, tarifario)
a bases de datos de Notion en modo lectura (solo visual).
"""
import json
from datetime import datetime
from typing import Optional

from app.database import (
    get_notion_cfg,
    save_notion_cfg,
    delete_notion_cfg,
    guardar_notion_url,
    get_notion_url,
)

try:
    from notion_client import Client as NotionClient
    from notion_client.errors import APIResponseError
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _rt(text: str) -> list:
    """Build a Notion rich_text block from a string (max 2000 chars)."""
    return [{"type": "text", "text": {"content": str(text)[:2000]}}]


def _client() -> Optional["NotionClient"]:
    if not NOTION_AVAILABLE:
        return None
    token = get_notion_cfg().get("notion_token", "")
    if not token:
        return None
    return NotionClient(auth=token)


def _lock(nc: "NotionClient", page_id: str) -> None:
    """Best-effort page lock (Enterprise only — silently ignored if unavailable)."""
    try:
        nc.pages.update(page_id=page_id, locked=True)
    except Exception:
        pass


def _callout_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": _rt(text),
            "icon": {"type": "emoji", "emoji": "⚠️"},
            "color": "yellow_background",
        },
    }


# ─── Estado de configuración ──────────────────────────────────────────────────

def is_notion_configured() -> bool:
    if not NOTION_AVAILABLE:
        return False
    cfg = get_notion_cfg()
    return bool(cfg.get("notion_token") and cfg.get("db_auditorias_id"))


def get_notion_db_urls() -> dict:
    """Return URLs for the three configured Notion databases."""
    cfg = get_notion_cfg()
    return {
        "auditorias": cfg.get("db_auditorias_url", ""),
        "siniestros":  cfg.get("db_siniestros_url", ""),
        "tarifario":   cfg.get("db_tarifario_url", ""),
    }


# ─── Configuración inicial ────────────────────────────────────────────────────

def configurar_notion(token: str, parent_page_id: str) -> dict:
    """
    Create all three Notion databases under *parent_page_id* and persist the
    config.  Returns {"ok": True, ...urls} or {"ok": False, "error": msg}.
    """
    if not NOTION_AVAILABLE:
        return {"ok": False, "error": "Librería notion-client no está instalada. Ejecuta: pip install notion-client"}

    try:
        nc = NotionClient(auth=token)
        # Validate token
        nc.users.me()

        # ── Auditorias ──
        db_aud = nc.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            icon={"type": "emoji", "emoji": "📋"},
            title=[{"type": "text", "text": {"content": "Auditorias — Facturase"}}],
            properties={
                "Factura":          {"title": {}},
                "Siniestro":        {"rich_text": {}},
                "Resultado":        {"select": {"options": [
                    {"name": "APROBADA",  "color": "green"},
                    {"name": "OBSERVADA", "color": "yellow"},
                    {"name": "RECHAZADA", "color": "red"},
                ]}},
                "Confianza":        {"number": {"format": "percent"}},
                "Items Aprobados":  {"number": {}},
                "Items Observados": {"number": {}},
                "Monto Total":      {"number": {"format": "dollar"}},
                "Discrepancias $":  {"number": {"format": "dollar"}},
                "Rev. Humana":      {"checkbox": {}},
                "Fecha":            {"date": {}},
                "Recomendacion":    {"rich_text": {}},
            },
        )

        # ── Siniestros ──
        db_sin = nc.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            icon={"type": "emoji", "emoji": "🚗"},
            title=[{"type": "text", "text": {"content": "Siniestros — Facturase"}}],
            properties={
                "ID Siniestro":    {"title": {}},
                "Tipo Accidente":  {"rich_text": {}},
                "Vehiculo":        {"rich_text": {}},
                "Poliza":          {"rich_text": {}},
                "Fecha Accidente": {"date": {}},
                "Partes Afectadas":{"rich_text": {}},
                "Descripcion":     {"rich_text": {}},
            },
        )

        # ── Tarifario ──
        db_tar = nc.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            icon={"type": "emoji", "emoji": "💲"},
            title=[{"type": "text", "text": {"content": "Tarifario — Facturase"}}],
            properties={
                "Codigo":        {"title": {}},
                "Descripcion":   {"rich_text": {}},
                "Precio Min":    {"number": {"format": "dollar"}},
                "Precio Max":    {"number": {"format": "dollar"}},
                "Unidad":        {"rich_text": {}},
                "Categoria":     {"select": {"options": [
                    {"name": "insumo",     "color": "blue"},
                    {"name": "mano_obra",  "color": "orange"},
                    {"name": "servicio",   "color": "purple"},
                ]}},
                "Vigente Desde": {"date": {}},
                "Vigente Hasta": {"date": {}},
            },
        )

        # Persist
        save_notion_cfg("notion_token",      token)
        save_notion_cfg("parent_page_id",    parent_page_id)
        save_notion_cfg("db_auditorias_id",  db_aud["id"])
        save_notion_cfg("db_siniestros_id",  db_sin["id"])
        save_notion_cfg("db_tarifario_id",   db_tar["id"])
        save_notion_cfg("db_auditorias_url", db_aud.get("url", ""))
        save_notion_cfg("db_siniestros_url", db_sin.get("url", ""))
        save_notion_cfg("db_tarifario_url",  db_tar.get("url", ""))

        return {
            "ok": True,
            "db_auditorias_url": db_aud.get("url", ""),
            "db_siniestros_url": db_sin.get("url", ""),
            "db_tarifario_url":  db_tar.get("url", ""),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def desconectar_notion() -> None:
    """Remove all Notion config from the local DB."""
    delete_notion_cfg()


# ─── Sincronizar auditoría ────────────────────────────────────────────────────

def sincronizar_auditoria(dictamen: dict, audit_db_id: int | None = None) -> Optional[str]:
    """
    Push one audit result to the Notion Auditorias database.
    Returns the Notion page URL (and persists it locally), or None on failure.
    """
    nc = _client()
    if not nc:
        return None
    cfg = get_notion_cfg()
    db_id = cfg.get("db_auditorias_id")
    if not db_id:
        return None

    ts = dictamen.get("timestamp", "")
    fecha_iso = ts[:10] if len(ts) >= 10 else datetime.now().strftime("%Y-%m-%d")

    discs_text = json.dumps(
        dictamen.get("discrepancias", []), indent=2, ensure_ascii=False
    )[:2000]

    page = nc.pages.create(
        parent={"database_id": db_id},
        properties={
            "Factura":          {"title": _rt(dictamen.get("factura_id", "—"))},
            "Siniestro":        {"rich_text": _rt(dictamen.get("siniestro_id", ""))},
            "Resultado":        {"select": {"name": dictamen.get("resultado", "OBSERVADA")}},
            "Confianza":        {"number": round(dictamen.get("confianza", 0), 4)},
            "Items Aprobados":  {"number": dictamen.get("items_aprobados", 0)},
            "Items Observados": {"number": dictamen.get("items_observados", 0)},
            "Monto Total":      {"number": dictamen.get("monto_total_factura", 0)},
            "Discrepancias $":  {"number": dictamen.get("monto_discrepancias", 0)},
            "Rev. Humana":      {"checkbox": bool(dictamen.get("requiere_revision_humana"))},
            "Fecha":            {"date": {"start": fecha_iso}},
            "Recomendacion":    {"rich_text": _rt(dictamen.get("recomendacion", ""))},
        },
        children=[
            _callout_block("Sincronizado desde Facturase. No editar manualmente — los cambios serán sobrescritos."),
            {"object": "block", "type": "heading_2",
             "heading_2": {"rich_text": _rt("Razonamiento del agente IA")}},
            {"object": "block", "type": "paragraph",
             "paragraph": {"rich_text": _rt(dictamen.get("razonamiento", ""))}},
            {"object": "block", "type": "heading_2",
             "heading_2": {"rich_text": _rt("Discrepancias detectadas")}},
            {"object": "block", "type": "code",
             "code": {"language": "json", "rich_text": _rt(discs_text)}},
        ],
    )
    _lock(nc, page["id"])
    url = page.get("url", "")
    if url and audit_db_id is not None:
        guardar_notion_url("auditoria", str(audit_db_id), url)
    return url or None


def sincronizar_todas_auditorias(auditorias: list[dict]) -> dict:
    """Bulk-sync all audits. Returns {"ok": int, "errores": int}."""
    ok = 0
    errores = 0
    for a in auditorias:
        try:
            url = sincronizar_auditoria(a, audit_db_id=a.get("id"))
            if url:
                ok += 1
            else:
                errores += 1
        except Exception:
            errores += 1
    return {"ok": ok, "errores": errores}


# ─── Sincronizar siniestro ────────────────────────────────────────────────────

def sincronizar_siniestro(siniestro: dict) -> Optional[str]:
    """Push a siniestro to Notion. Returns page URL or None."""
    nc = _client()
    if not nc:
        return None
    cfg = get_notion_cfg()
    db_id = cfg.get("db_siniestros_id")
    if not db_id:
        return None

    page = nc.pages.create(
        parent={"database_id": db_id},
        properties={
            "ID Siniestro":     {"title": _rt(siniestro["id"])},
            "Tipo Accidente":   {"rich_text": _rt(siniestro.get("tipo_accidente", ""))},
            "Vehiculo":         {"rich_text": _rt(siniestro.get("vehiculo", ""))},
            "Poliza":           {"rich_text": _rt(siniestro.get("poliza", ""))},
            "Fecha Accidente":  {"date": {"start": siniestro.get("fecha_accidente", "")}},
            "Partes Afectadas": {"rich_text": _rt(", ".join(siniestro.get("partes_afectadas", [])))},
            "Descripcion":      {"rich_text": _rt(siniestro.get("descripcion", ""))},
        },
        children=[
            _callout_block("Sincronizado desde Facturase. No editar manualmente."),
        ],
    )
    _lock(nc, page["id"])
    url = page.get("url", "")
    if url:
        guardar_notion_url("siniestro", siniestro["id"], url)
    return url or None


def sincronizar_todos_siniestros(siniestros: list[dict]) -> dict:
    ok = 0
    errores = 0
    for s in siniestros:
        try:
            url = sincronizar_siniestro(s)
            if url:
                ok += 1
            else:
                errores += 1
        except Exception:
            errores += 1
    return {"ok": ok, "errores": errores}


# ─── Sincronizar tarifario ────────────────────────────────────────────────────

def sincronizar_tarifario_items(items: list[dict]) -> dict:
    """Bulk-sync all tarifario items. Returns {"ok": int, "errores": int}."""
    nc = _client()
    if not nc:
        return {"ok": 0, "errores": 0, "error": "Notion no configurado"}
    cfg = get_notion_cfg()
    db_id = cfg.get("db_tarifario_id")
    if not db_id:
        return {"ok": 0, "errores": 0, "error": "BD tarifario no configurada"}

    ok = 0
    errores = 0
    for item in items:
        try:
            page = nc.pages.create(
                parent={"database_id": db_id},
                properties={
                    "Codigo":        {"title": _rt(item["codigo"])},
                    "Descripcion":   {"rich_text": _rt(item.get("descripcion", ""))},
                    "Precio Min":    {"number": item.get("precio_min", 0)},
                    "Precio Max":    {"number": item.get("precio_max", 0)},
                    "Unidad":        {"rich_text": _rt(item.get("unidad", ""))},
                    "Categoria":     {"select": {"name": item.get("categoria", "insumo")}},
                    "Vigente Desde": {"date": {"start": item.get("vigente_desde", "")}},
                    "Vigente Hasta": {"date": {"start": item.get("vigente_hasta", "")}},
                },
            )
            _lock(nc, page["id"])
            ok += 1
        except Exception:
            errores += 1
    return {"ok": ok, "errores": errores}
