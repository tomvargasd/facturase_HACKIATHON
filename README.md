# Facturase — Auditoria Inteligente de Facturas Automotrices

Sistema de auditoría de facturas de talleres automotrices impulsado por IA (Google Gemini). Analiza cada factura contra el tarifario autorizado y el expediente del siniestro, emitiendo un dictamen estructurado antes de que el ajustador humano intervenga. Incluye dashboard web, autenticación, cola de procesamiento en lote y sincronización con Notion.

> Desarrollado para el **HackIAThon 2026** — Equipo Facturase  
> Dominio de producción: [facturase.dpdns.org](https://facturase.dpdns.org)  
> Repositorio: [github.com/tomvargasd/facturase_HACKIATHON](https://github.com/tomvargasd/facturase_HACKIATHON)

---

## Características principales

| Módulo | Descripción |
|---|---|
| **Dashboard** | Métricas en tiempo real, gráficos de distribución, acciones rápidas |
| **Auditar Factura** | Análisis individual con IA (PDF o demo JSON) |
| **Cola de revisión** | Acumula casos y los procesa en lote con un clic |
| **Historial** | Registro completo de todas las auditorías ejecutadas |
| **Siniestros** | Gestión de expedientes (crear, consultar, eliminar) |
| **Tarifario** | Administración de precios de referencia |
| **Notion Sync** | Sincronización de datos a Notion en modo solo lectura |
| **Tour guiado** | Tutorial interactivo en el primer acceso |

---

## Arquitectura

```
Factura (PDF / JSON)
        │
        ▼
┌───────────────────┐
│   Extractor       │  Gemini Vision → JSON estructurado
└────────┬──────────┘
         │
    ┌────┴────────────────────────────────┐
    │                                     │
    ▼                                     ▼
Motor de Precios              Motor de Duplicados
(vs. tarifario SQLite)        (Counter por código)
    │                                     │
    └──────────────┬──────────────────────┘
                   │
                   ▼
         Motor de Coherencia
         (Gemini analiza ítems vs. siniestro)
                   │
                   ▼
         Orquestador (Gemini)
         → Dictamen final razonado
                   │
                   ▼
          SQLite (auditoria.db)
                   │
          ┌────────┴────────┐
          ▼                 ▼
     FastAPI REST      Streamlit Dashboard
                            │
                            ▼
                       Notion Sync
                    (solo lectura visual)
```

---

## Stack tecnológico

- **Backend:** Python 3.12, FastAPI, Uvicorn
- **Frontend:** Streamlit 1.40+
- **IA:** Google Gemini 2.5 Flash (`google-genai`)
- **Base de datos:** SQLite (`auditoria.db`)
- **Visualización:** Plotly
- **Integración:** Notion API (`notion-client`)
- **Servidor:** Apache 2 + Let's Encrypt SSL (Contabo VPS)

---

## Estructura del proyecto

```
├── app/
│   ├── config.py          # Variables de entorno y constantes
│   ├── database.py        # SQLite: tablas, CRUD, autenticación
│   ├── extractor.py       # Extracción de facturas PDF con Gemini Vision
│   ├── main.py            # API REST FastAPI
│   ├── models.py          # Modelos Pydantic
│   ├── notion_sync.py     # Integración Notion
│   ├── orquestador.py     # Pipeline de auditoría (5 pasos)
│   └── verificadores.py   # Motores de precio, duplicados y coherencia
├── dashboard/
│   ├── login.py           # Pantalla de login + captcha matemático
│   ├── streamlit_app.py   # Aplicación principal
│   └── styles.py          # CSS compartido
├── data/
│   └── demo_data.py       # 30 ítems tarifario + 3 siniestros + 3 facturas demo
├── scripts/
│   ├── seed_database.py   # Inicializar BD con datos demo
│   └── add_user.py        # CLI para agregar usuarios
├── .env.example           # Plantilla de variables de entorno
├── requirements.txt
└── auditoria.db           # Base de datos SQLite (generada al iniciar)
```

---

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/tomvargasd/facturase_HACKIATHON.git
cd facturase_HACKIATHON

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key de Gemini
cp .env.example .env
# Edita .env y agrega: GEMINI_API_KEY=AIza...

# 5. Inicializar la base de datos con datos de demo
python -m scripts.seed_database

# 6. Crear el primer usuario administrador
python scripts/add_user.py
```

---

## Ejecutar la aplicación

```bash
# Dashboard web (recomendado)
streamlit run dashboard/streamlit_app.py

# API REST (opcional, para integraciones externas)
uvicorn app.main:app --reload --port 8000
```

La app estará disponible en `http://localhost:8501`.

---

## Despliegue en producción (Ubuntu + Apache)

Ver [MANUAL.md](MANUAL.md) para instrucciones completas de despliegue con SSL, Apache y servicio systemd.

---

## Variables de entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `GEMINI_API_KEY` | API Key de Google AI Studio | Sí |
| `NOTION_TOKEN` | Token de integración de Notion | No (configurable desde UI) |
| `NOTION_PARENT_PAGE_ID` | ID de la página padre en Notion | No (configurable desde UI) |

---

## Licencia

MIT — Desarrollado como prueba oficial del HackIAThon 2026.

Abre `http://localhost:8501` en tu navegador.

**Flujo de demo (3 escenarios):**

| Factura   | Siniestro      | Resultado esperado |
|-----------|----------------|--------------------|
| DEMO-001  | SIN-2025-001   | ✅ APROBADA         |
| DEMO-002  | SIN-2025-002   | ⚠️ OBSERVADA        |
| DEMO-003  | SIN-2025-003   | ❌ RECHAZADA         |

### API REST

```bash
uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

**Auditar con factura JSON (modo demo):**
```bash
curl -X POST http://localhost:8000/auditar \
  -F "siniestro_id=SIN-2025-001" \
  -F 'factura_json={"numero_factura":"FAC-001","fecha":"2025-04-18","taller":"Taller X","items":[...],"total_factura":1000}'
```

**Auditar con PDF real:**
```bash
curl -X POST http://localhost:8000/auditar \
  -F "siniestro_id=SIN-2025-001" \
  -F "factura_pdf=@factura.pdf"
```

---

## Estructura del proyecto

```
.
├── app/
│   ├── config.py          # Variables de entorno y constantes
│   ├── database.py        # SQLite — conexiones y queries
│   ├── models.py          # Schemas Pydantic
│   ├── extractor.py       # Claude Vision — OCR de facturas
│   ├── verificadores.py   # 3 motores de verificación
│   ├── orquestador.py     # Pipeline principal + dictamen Claude
│   └── main.py            # FastAPI
├── dashboard/
│   └── streamlit_app.py   # Dashboard web
├── data/
│   └── demo_data.py       # Tarifario + siniestros + facturas demo
├── scripts/
│   └── seed_database.py   # Inicializa la BD
├── requirements.txt
├── .env.example
└── PLAN.md
```

---

## Schema del dictamen

```json
{
  "factura_id": "FAC-2025-00341",
  "siniestro_id": "SIN-2025-001",
  "resultado": "OBSERVADA",
  "confianza": 0.87,
  "items_aprobados": 14,
  "items_observados": 2,
  "monto_total_factura": 20710.00,
  "monto_discrepancias": 710.00,
  "discrepancias": [
    {
      "tipo": "precio_excedido",
      "item": "Parabrisas delantero OEM",
      "cobrado": 3800.00,
      "tarifario_max": 3200.00,
      "diferencia": 600.00
    }
  ],
  "requiere_revision_humana": true,
  "razonamiento": "Se detectó 1 ítem con precio fuera del tarifario...",
  "recomendacion": "Solicitar al taller factura rectificativa...",
  "timestamp": "2025-05-15T10:30:00Z"
}
```

---

## Umbral de revisión humana

El sistema escala automáticamente a revisión humana cuando:
- Confianza del agente < 75%
- Monto total de discrepancias > $500 MXN
- Resultado = `RECHAZADA`

Configurable en `app/config.py`.
