def rawStyles():
    return """
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090f1a 0%, #0d1829 40%, #0b1422 100%) !important;
    border-right: 1px solid #162236;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #8fadc8 !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: transparent !important; border: none !important;
    color: #5a7d9a !important; text-align: left !important;
    padding: 0.58rem 1.4rem !important; border-radius: 0 !important;
    font-size: 0.84rem !important; font-weight: 500 !important;
    transition: all 0.12s ease !important; margin-bottom: 0 !important;
    border-left: 3px solid transparent !important; letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.08) !important;
    color: #c8ddf0 !important; border-left-color: #3b82f6 !important;
}

/* ── Nav menu: SVG anchor links ── */
.nav-item-link {
    display: flex !important;
    align-items: center !important;
    gap: 9px !important;
    padding: 0.58rem 1.4rem !important;
    text-decoration: none !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    border-left: 3px solid transparent !important;
    transition: all 0.12s ease !important;
    color: #5a7d9a !important;
    cursor: pointer !important;
}
.nav-item-link svg { flex-shrink: 0; }
.nav-item-link span { flex: 1; }
.nav-item-link:hover {
    background: rgba(59,130,246,0.08) !important;
    color: #c8ddf0 !important;
    border-left-color: #3b82f6 !important;
    text-decoration: none !important;
}
.nav-item-link.nav-active {
    background: rgba(59,130,246,0.12) !important;
    color: #c8ddf0 !important;
    border-left-color: #3b82f6 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1rem 1.25rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.74rem !important; color: #64748b !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important; font-weight: 700 !important; color: #0f172a !important;
}

/* ── Page elements ── */
.page-header {
    display: flex; align-items: center; gap: 0.75rem;
    margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e2e8f0;
}
.page-header h2 { margin:0; font-size:1.35rem; font-weight:700; color:#0f172a; }
.page-header p  { margin:0; font-size:0.82rem; color:#64748b; }

.badge { display:inline-flex; align-items:center; gap:0.35rem; padding:0.28rem 0.9rem; border-radius:9999px; font-weight:700; font-size:0.84rem; }
.badge-APROBADA  { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.badge-OBSERVADA { background:#fef9c3; color:#854d0e; border:1px solid #fde047; }
.badge-RECHAZADA { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }

.dictamen-card {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:1.25rem; margin-bottom:1rem; box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.alerta-revision {
    background:#fff7ed; border:1px solid #fed7aa; border-left:4px solid #f97316;
    border-radius:8px; padding:0.65rem 1rem; color:#9a3412; font-size:0.85rem; margin:0.6rem 0;
}
.alerta-ok {
    background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #22c55e;
    border-radius:8px; padding:0.65rem 1rem; color:#166534; font-size:0.85rem; margin:0.6rem 0;
}

/* ── Quick-action cards (enhanced) ── */
.quick-card {
    background: linear-gradient(135deg, #fff 60%, #f0f6ff);
    border: 1.5px solid #bfdbfe;
    border-radius: 16px;
    padding: 1.25rem 1rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(59,130,246,0.10);
    margin-bottom: 0.25rem;
    transition: box-shadow 0.15s;
}
.quick-card:hover { box-shadow: 0 4px 20px rgba(59,130,246,0.18); }

.queue-item {
    background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
    padding:0.65rem 1rem; margin-bottom:0.4rem;
}

/* ── Login ── */
.login-card {
    background:#fff; border-radius:20px; padding:2.5rem 2rem;
    box-shadow:0 20px 60px rgba(0,0,0,0.10); border:1px solid #e2e8f0;
}

/* ── Misc ── */
@media (max-width:768px) {
    .page-header h2 { font-size:1.1rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:1.1rem !important; }
}
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
[data-testid="stExpander"]  { border:1px solid #e2e8f0 !important; border-radius:10px !important; }
.stButton > button[kind="primary"] {
    background:#1856b4 !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
}
.stButton > button[kind="primary"]:hover { background:#1447a0 !important; }
#MainMenu, footer { visibility:hidden; }

/* ── Sidebar secondary buttons (altbuton → blue) ── */
.altbuton .stButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0.55rem 1.2rem !important;
    transition: background 0.15s !important;
}
.altbuton .stButton > button:hover {
    background: #1d4ed8 !important;
}

/* ── Equipo button (standout cyan) ── */
.equipobtn .stButton > button {
    background: linear-gradient(90deg, #0284c7, #38bdf8) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.55rem 1.2rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 2px 8px rgba(2,132,199,0.28) !important;
    transition: box-shadow 0.15s, background 0.15s !important;
}
.equipobtn .stButton > button:hover {
    background: linear-gradient(90deg, #0369a1, #0ea5e9) !important;
    box-shadow: 0 4px 14px rgba(2,132,199,0.40) !important;
}

/* ── Tour button (standout green) ── */
.tourbtn .stButton > button {
    background: linear-gradient(90deg, #059669, #10b981) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.22) !important;
    transition: box-shadow 0.15s, background 0.15s !important;
}
.tourbtn .stButton > button:hover {
    background: linear-gradient(90deg, #047857, #059669) !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.32) !important;
}

/* ── Quick action buttons ── */
.qa-btn-nueva .stButton > button {
    background: linear-gradient(90deg, #1856b4, #2563eb) !important;
    color: #fff !important; border-radius: 8px !important;
    font-weight: 700 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.22) !important;
}
.qa-btn-cola .stButton > button {
    background: linear-gradient(90deg, #5b21b6, #7c3aed) !important;
    color: #fff !important; border-radius: 8px !important;
    font-weight: 700 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.22) !important;
}
.qa-btn-siniestro .stButton > button {
    background: linear-gradient(90deg, #0e7490, #0891b2) !important;
    color: #fff !important; border-radius: 8px !important;
    font-weight: 700 !important; border: none !important;
    box-shadow: 0 2px 8px rgba(8,145,178,0.22) !important;
}

/* ══════════════════════════════════════════════════
   TOUR OVERLAY
   ══════════════════════════════════════════════════ */
#facturase-tour-overlay {
    position: fixed; inset: 0; z-index: 9998;
    pointer-events: none;
}
#facturase-tour-overlay.active { pointer-events: all; }

/* dark backdrop with cutout hole via box-shadow */
#facturase-tour-spotlight {
    position: fixed; z-index: 9999;
    border-radius: 10px;
    box-shadow:
        0 0 0 4px rgba(59,130,246,0.8),
        0 0 0 9999px rgba(0,0,0,0.68);
    transition: all 0.28s cubic-bezier(.4,0,.2,1);
    pointer-events: none;
}

#facturase-tour-card {
    position: fixed; z-index: 10000;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.22);
    padding: 1.4rem 1.6rem 1.2rem 1.6rem;
    width: 340px;
    max-width: 92vw;
    transition: all 0.28s cubic-bezier(.4,0,.2,1);
}
#facturase-tour-card .tc-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.55rem;
}
#facturase-tour-card .tc-step {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #3b82f6;
    background: #eff6ff; padding: 2px 8px; border-radius: 9999px;
}
#facturase-tour-card .tc-title {
    font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.35rem;
}
#facturase-tour-card .tc-desc {
    font-size: 0.83rem; color: #475569; line-height: 1.55; margin-bottom: 1rem;
}
#facturase-tour-card .tc-nav {
    display: flex; gap: 0.5rem; align-items: center;
}
#facturase-tour-card .tc-nav button {
    border: none; cursor: pointer; border-radius: 8px;
    font-size: 0.82rem; font-weight: 600; padding: 0.42rem 0.9rem;
    transition: background 0.12s;
}
#facturase-tour-card .tc-btn-prev {
    background: #f1f5f9; color: #475569;
}
#facturase-tour-card .tc-btn-prev:hover { background: #e2e8f0; }
#facturase-tour-card .tc-btn-next {
    background: #2563eb; color: #fff; flex: 1;
}
#facturase-tour-card .tc-btn-next:hover { background: #1d4ed8; }
#facturase-tour-card .tc-btn-skip {
    background: transparent; color: #94a3b8; font-size: 0.76rem;
    padding: 0.3rem 0.5rem; margin-left: auto;
}
#facturase-tour-card .tc-btn-skip:hover { color: #64748b; }
#facturase-tour-card .tc-dots {
    display: flex; gap: 5px; align-items: center;
}
#facturase-tour-card .tc-dot {
    width: 7px; height: 7px; border-radius: 50%; background: #e2e8f0;
    transition: background 0.15s, transform 0.15s;
}
#facturase-tour-card .tc-dot.active {
    background: #2563eb; transform: scale(1.3);
}
</style>
"""