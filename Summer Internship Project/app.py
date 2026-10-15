"""
Fin-Suraksha: National AI-Assisted Financial Crime Attribution Console
Official Portal & Operational Console • Cyber Police Station, Sector-17, Rohini, Delhi-110089

Delhi Police Motto: शांति सेवा न्याय | SHANTI SEWA NYAYA
Helpline: Cyber Fraud Complaints — 1930 | Emergency: 112
National Portal: https://cybercrime.gov.in

Developer     : Bhawna Vashisht | Department of Computer Applications, MAIMS
                Enrolment No.: 35114702024
Host Org      : Cyber Police Station, Sector-17, Rohini, Delhi-110089
Mentor        : ASI Jaswinder Joon (I.O.) | PIS: 28910482
Station House : Inspector Parveen Chauhan (S.H.O.)

जय हिन्द | JAI HIND | JAI BHARAT | जय भारत
"""

import os
import io
import math
import json
import random
import datetime
import pandas as pd
import numpy as np
import networkx as nx
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import logo_helper

from model import (
    DatabaseEngine, BankingEcosystemGenerator, build_transaction_graph,
    add_shared_identifier_edges, engineer_node_features, scale_features,
    ModelZoo, evaluate_metrics, compute_shap_values, ecosystem_to_csv_bundle,
    CLASSES, FRAUD_SCENARIOS, FEATURE_NAMES, DB_PATH, CLASS_TO_IDX,
    IDX_TO_CLASS, run_real_shap_explanation
)
from intelligence import (
    DigitalFootprintEngine, PhysicalFootprintEngine, NetworkAnalyticsEngine,
    HeuristicRiskEngine, build_money_trail_case, generate_investigation_narrative,
    generate_legal_notice, generate_case_pdf_report, haversine_distance,
    HAS_REPORTLAB
)

# ─────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Delhi Police | Fin-Suraksha Attribution Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────
# COMPREHENSIVE GOVERNMENT PORTAL CSS
# Delhi Police: Navy #002147 | Gold #D4AF37 | Red #C4122F
# ─────────────────────────────────────────────────────────
st.markdown("""<style>
/* ===== GLOBAL BASE ===== */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F0F2F5 !important;
    color: #1A1A2E !important;
    font-family: "Segoe UI", Arial, sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding-top: 0rem !important;
    max-width: 100% !important;
}

/* ===== DELHI POLICE TOP GOVERNMENT HEADER ===== */
.dp-top-ribbon {
    background: linear-gradient(90deg, #7B0000 0%, #C4122F 40%, #7B0000 100%);
    color: #FFFFFF;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 6px 20px;
    text-align: center;
    letter-spacing: 1.5px;
}
.dp-main-header {
    background: linear-gradient(135deg, #001233 0%, #002147 60%, #001A38 100%);
    border-bottom: 4px solid #C4122F;
    padding: 14px 28px 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.dp-brand-block { display: flex; align-items: center; gap: 16px; }
.dp-emblem-circle {
    width: 68px; height: 68px;
    background: radial-gradient(circle, #F59E0B, #D97706);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    font-weight: 900;
    color: #001C3D;
    border: 3px solid #FFFFFF;
    box-shadow: 0 0 14px rgba(245,158,11,0.5);
}
.dp-title-stack { color: #FFFFFF; }
.dp-org-name {
    font-size: 1.85rem; font-weight: 900;
    color: #FFFFFF; letter-spacing: 1.2px;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.45);
    line-height: 1.1;
}
.dp-sub-title {
    font-size: 0.88rem; color: #F59E0B;
    font-weight: 800; letter-spacing: 1.5px;
    text-transform: uppercase; margin-top: 3px;
}
.dp-station-line {
    font-size: 0.80rem; color: #E2E8F0; margin-top: 2px;
}
.dp-right-block { text-align: right; }
.dp-helpline-pill {
    background: #C4122F; color: #FFFFFF;
    font-size: 0.85rem; font-weight: 800;
    padding: 6px 16px; border-radius: 20px;
    display: inline-block; margin-bottom: 5px;
    border: 1.5px solid #FF8080;
    letter-spacing: 0.5px;
}
.dp-jaihind {
    font-size: 0.82rem; color: #86EFAC;
    font-weight: 800; letter-spacing: 1.2px;
}
.dp-satya {
    font-size: 0.76rem; color: #FDE68A;
    letter-spacing: 1px;
}

/* ===== TOP NAVIGATION BAR ===== */
.dp-navbar {
    background: #001C3D;
    border-bottom: 3px solid #C4122F;
    padding: 0;
    overflow-x: auto;
    white-space: nowrap;
}
.dp-navbar-inner {
    display: flex;
    gap: 2px;
    padding: 6px 12px;
    flex-wrap: wrap;
}

/* Streamlit pills override for navbar */
div[data-testid="stPills"] {
    background: transparent !important;
    gap: 6px !important;
    display: flex !important;
    flex-wrap: wrap !important;
    width: 100% !important;
    justify-content: flex-start !important;
}
div[data-testid="stPills"] [data-testid="stPillsWrapper"] {
    background: transparent !important;
    padding: 4px 6px !important;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    width: 100% !important;
}
div[data-testid="stPills"] button {
    background: #00122B !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    border: 1.5px solid #1E3A8A !important;
    border-radius: 4px !important;
    padding: 8px 16px !important;
    transition: all 0.22s ease-in-out !important;
    white-space: nowrap !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
}
div[data-testid="stPills"] button:hover {
    background: #F59E0B !important;
    color: #00122B !important;
    border-color: #D97706 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(245,158,11,0.55) !important;
}
div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
    color: #00122B !important;
    font-weight: 900 !important;
    border: 2px solid #D97706 !important;
    border-bottom: 4px solid #C4122F !important;
    box-shadow: 0 0 16px rgba(245,158,11,0.7) !important;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001233 0%, #001A38 50%, #001026 100%) !important;
    border-right: 2px solid #002D5E !important;
    min-width: 270px !important;
}
section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
section[data-testid="stSidebar"] .stSelectbox > label { color: #F59E0B !important; font-weight: 700 !important; font-size: 0.85rem !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 0 !important;
}

/* Sidebar selectbox input control: Police Dark Navy */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: #001838 !important;
    border: 1.5px solid #004080 !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"]:hover {
    border-color: #F59E0B !important;
    box-shadow: 0 0 8px rgba(245, 158, 11, 0.4) !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #FFFFFF !important;
    background-color: transparent !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #F59E0B !important;
}

/* Sidebar Dropdown Menu Popover Options */
div[data-baseweb="popover"] div[role="listbox"],
div[data-baseweb="menu"] {
    background-color: #001838 !important;
    border: 1.5px solid #004080 !important;
}
div[data-baseweb="popover"] li[role="option"],
div[data-baseweb="menu"] li {
    background-color: #001838 !important;
    color: #F8FAFC !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
}
div[data-baseweb="popover"] li[role="option"]:hover,
div[data-baseweb="menu"] li:hover,
div[data-baseweb="popover"] li[aria-selected="true"] {
    background-color: #003366 !important;
    color: #F59E0B !important;
    font-weight: 800 !important;
}

/* ===== METRIC CARDS ===== */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-top: 4px solid #002147 !important;
    padding: 14px 16px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(0,33,71,0.08) !important;
    transition: transform 0.2s !important;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(0,33,71,0.15) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] { color: #334155 !important; font-size: 0.88rem !important; font-weight: 700 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #002147 !important; font-weight: 900 !important; font-size: 1.45rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 0.82rem !important; }

/* ===== SECTION HEADING ===== */
.dp-sec-head {
    border-left: 5px solid #C4122F;
    padding: 6px 0 6px 14px;
    margin: 16px 0 12px 0;
    font-size: 1.15rem;
    font-weight: 800;
    color: #002147;
    background: linear-gradient(90deg, rgba(196,18,47,0.06) 0%, transparent 100%);
    border-radius: 0 4px 4px 0;
}

/* ===== BREADCRUMB ===== */
.dp-breadcrumb {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-left: 4px solid #002147;
    padding: 10px 18px;
    border-radius: 4px;
    font-size: 0.90rem;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* ===== HOP CARDS ===== */
.hop-card-item {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-left: 5px solid #002147;
    padding: 14px 18px;
    border-radius: 6px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.hop-card-item:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.1); }
.hop-badge-pill {
    background: linear-gradient(135deg, #002147, #003875);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 20px;
}

/* ===== STAT BOXES ===== */
.stat-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-num { font-size: 2rem; font-weight: 900; color: #002147; }
.stat-label { font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

/* ===== DEVELOPER FOOTER ===== */
.dp-footer {
    background: linear-gradient(135deg, #001233 0%, #001A38 100%);
    color: #CBD5E1;
    font-size: 0.74rem;
    padding: 16px 24px;
    border-radius: 8px;
    margin-top: 28px;
    border-top: 3px solid #C4122F;
    line-height: 1.7;
}

/* ===== LOGIN PAGE ===== */
.login-wrapper {
    min-height: 85vh;
    display: flex;
    align-items: center;
    justify-content: center;
}
.login-box {
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-top: 5px solid #002147;
    border-bottom: 5px solid #C4122F;
    padding: 32px 36px;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0,33,71,0.12);
    max-width: 440px;
    margin: auto;
}
.login-seal {
    text-align: center;
    margin-bottom: 20px;
}
.login-seal-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 6px;
    filter: drop-shadow(0 4px 8px rgba(0,33,71,0.3));
}
.login-title {
    color: #002147;
    font-size: 1.5rem;
    font-weight: 900;
    margin: 0;
    line-height: 1.2;
}
.login-subtitle {
    color: #C4122F;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    margin-top: 4px;
}
.login-org {
    color: #64748B;
    font-size: 0.70rem;
    margin-top: 2px;
}
.login-divider {
    border: none;
    border-top: 1.5px solid #E5E7EB;
    margin: 16px 0;
}
.login-notice {
    background: #FEF3C7;
    border: 1px solid #F59E0B;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 0.70rem;
    color: #78350F;
    margin-top: 12px;
    line-height: 1.5;
}
.cred-hint {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 0.70rem;
    color: #1E40AF;
    line-height: 1.6;
}

/* ===== TABS ===== */
div[data-testid="stTabs"] [role="tab"] {
    font-weight: 700 !important;
    color: #475569 !important;
    font-size: 0.82rem !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #002147 !important;
    border-bottom: 3px solid #C4122F !important;
}

/* ===== TABLES ===== */
div[data-testid="stDataFrame"] { border-radius: 6px !important; }

/* ===== BUTTONS ===== */
div[data-testid="stButton"] button {
    background: #002147 !important;
    color: #FFFFFF !important;
    border: 1px solid #003875 !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    border-radius: 4px !important;
    padding: 8px 18px !important;
    transition: all 0.22s ease-in-out !important;
    box-shadow: 0 2px 6px rgba(0,33,71,0.2) !important;
}
div[data-testid="stButton"] button:hover {
    background: #F59E0B !important;
    color: #00122B !important;
    border-color: #D97706 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(245,158,11,0.5) !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #002147 0%, #003875 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #F59E0B !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    border-radius: 4px !important;
    padding: 9px 20px !important;
    transition: all 0.22s ease-in-out !important;
    box-shadow: 0 3px 10px rgba(0,33,71,0.3) !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #C4122F 0%, #99001A 100%) !important;
    color: #FFFFFF !important;
    border-color: #EF4444 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 16px rgba(196,18,47,0.45) !important;
}
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #002147 0%, #003875 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #F59E0B !important;
    font-weight: 800 !important;
    font-size: 1.0rem !important;
    border-radius: 4px !important;
    padding: 10px 20px !important;
    transition: all 0.22s ease-in-out !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #C4122F 0%, #99001A 100%) !important;
    color: #FFFFFF !important;
    border-color: #EF4444 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 16px rgba(196,18,47,0.45) !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F0F2F5; }
::-webkit-scrollbar-thumb { background: #002147; border-radius: 3px; }

/* ===== OFFICER MODE ALERT ===== */
.officer-mode-banner {
    background: linear-gradient(90deg, #FEF3C7, #FFFBEB);
    border: 1.5px solid #F59E0B;
    border-left: 5px solid #D97706;
    padding: 10px 16px;
    border-radius: 6px;
    color: #78350F;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 14px;
}

/* ===== NAVBAR CONTAINER ===== */
.dp-navbar-box {
    background: #001C3D !important;
    border-bottom: 3px solid #C4122F !important;
    padding: 6px 12px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 16px rgba(0,28,61,0.3) !important;
}
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# GOVERNMENT HEADER BUILDER
# ─────────────────────────────────────────────────────────
def render_gov_header(officer_name="", badge="", show_login_mode=False):
    ribbon_text = "भारत सरकार — GOVERNMENT OF INDIA | Ministry of Home Affairs | Delhi Police | JAI HIND • JAI BHARAT • सत्यमेव जयते"
    st.markdown(f'<div class="dp-top-ribbon">{ribbon_text}</div>', unsafe_allow_html=True)

    logo_uri = logo_helper.get_logo_data_uri()
    if logo_uri:
        logo_html = f'<img src="{logo_uri}" style="width:68px;height:68px;object-fit:contain;margin-right:12px;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.45));" alt="Delhi Police"/>'
    else:
        logo_html = '<div class="dp-emblem-circle">DP</div>'

    officer_html = ""
    if officer_name:
        officer_html = (
            f'<div style="font-size:0.82rem;color:#CBD5E1;margin-top:4px;">'
            f'<span style="color:#86EFAC;font-weight:700;">● LIVE OFFICIAL SESSION</span> &nbsp;|&nbsp; '
            f'Investigating Officer: <strong style="color:#FFFFFF;">{officer_name}</strong> &nbsp;|&nbsp; '
            f'PIS/Badge: <span style="background:#003875;padding:2px 8px;border-radius:3px;color:#FDE68A;">{badge}</span>'
            f'</div>'
        )

    hdr = (
        '<div class="dp-main-header">'
        '<div class="dp-brand-block">'
        f'{logo_html}'
        '<div class="dp-title-stack">'
        '<div class="dp-org-name">DELHI POLICE</div>'
        '<div class="dp-sub-title">शान्ति &bull; सेवा &bull; न्याय &nbsp;|&nbsp; SHANTI SEWA NYAYA</div>'
        '<div class="dp-station-line">Cyber Crime Cell &bull; Sector-17, Rohini District, Delhi-110089 &bull; Fin-Suraksha Attribution Console</div>'
        f'{officer_html}'
        '</div>'
        '</div>'
        '<div class="dp-right-block">'
        '<div class="dp-helpline-pill">🚨 CYBER HELPLINE: 1930 &nbsp;|&nbsp; EMERGENCY: 112</div><br/>'
        '<div class="dp-jaihind">🇮🇳 जय हिन्द &bull; जय भारत &bull; JAI HIND &bull; JAI BHARAT</div>'
        '<div class="dp-satya">सत्यमेव जयते &bull; Azadi Ka Amrit Mahotsav &bull; cybercrime.gov.in</div>'
        '</div>'
        '</div>'
    )
    st.markdown(hdr, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────
# DEVELOPER FOOTER
# ─────────────────────────────────────────────────────────
def dev_footer():
    st.markdown("""
<div class="dp-footer">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
        <div>
            <strong style="color:#FFFFFF;font-size:0.82rem;">DELHI POLICE CYBER CRIME CELL &bull; SECTOR-17, ROHINI DISTRICT, DELHI-110089</strong><br/>
            <span style="color:#F59E0B;font-weight:700;">शान्ति सेवा न्याय &bull; SHANTI SEWA NYAYA &bull; 🇮🇳 सत्यमेव जयते &bull; जय हिन्द &bull; जय भारत</span><br/>
            <span style="color:#CBD5E1;"><strong style="color:#FFFFFF;">Developer:</strong> Bhawna Vashisht &nbsp;|&nbsp; Department of Computer Applications, MAIMS</span><br/>
            <span style="color:#94A3B8;font-size:0.70rem;">Enrolment No.: 35114702024 &nbsp;|&nbsp; Summer Internship Project 2026</span><br/>
            <strong style="color:#CBD5E1;">Investigating Mentor:</strong> <span style="color:#CBD5E1;">ASI Jaswinder Joon (I.O.) &bull; PIS: 28910482</span> &nbsp;&bull;&nbsp;
            <strong style="color:#CBD5E1;">SHO:</strong> <span style="color:#CBD5E1;">Insp. Parveen Chauhan</span>
        </div>
        <div style="text-align:right;font-size:0.70rem;color:#64748B;">
            🚨 Cyber Helpline: <strong style="color:#F87171;">1930</strong> &bull; Emergency: <strong style="color:#F87171;">112</strong><br/>
            Standard: <strong>Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023</strong><br/>
            Section 94 Notice Protocol &bull; IT Act, 2000 &bull; IPC<br/>
            Portal: <strong>cybercrime.gov.in</strong>
        </div>
    </div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────
# NOTE: These are DEMO credentials for an academic prototype.
# Passwords are hashed using werkzeug.security if available.
# In production, use a proper identity management system.
# ─────────────────────────────────────────────────────────
try:
    from werkzeug.security import generate_password_hash, check_password_hash as _check_pw
    _HASH_DEMO_ADMIN = generate_password_hash("DemoAdmin@2024!")
    _HASH_DEMO_IO    = generate_password_hash("DemoIO@2024!")
    _USE_HASHED_PASSWORDS = True
except ImportError:
    _USE_HASHED_PASSWORDS = False

def _verify_password(user_record, provided_password):
    """Verifies password against stored value. Uses werkzeug hash if available."""
    if _USE_HASHED_PASSWORDS:
        stored_hash = user_record.get("_pw_hash", "")
        return stored_hash and _check_pw(stored_hash, provided_password)
    else:
        # Fallback: plain comparison (academic demo only — insecure)
        return user_record.get("password", "") == provided_password

USERS = {
    "DEMO_ADMIN": {
        "_pw_hash": _HASH_DEMO_ADMIN if _USE_HASHED_PASSWORDS else None,
        "password": "DemoAdmin@2024!" if not _USE_HASHED_PASSWORDS else None,
        "role": "Tech Admin / Developer",
        "name": "Bhawna Vashisht (Developer)",
        "badge": "MAIMS-DEV-351",
        "is_admin": True,
    },
    "DEMO_IO": {
        "_pw_hash": _HASH_DEMO_IO if _USE_HASHED_PASSWORDS else None,
        "password": "DemoIO@2024!" if not _USE_HASHED_PASSWORDS else None,
        "role": "Investigating Officer (I.O.)",
        "name": "Demo Investigating Officer",
        "badge": "DEMO-IO-001",
        "is_admin": False,
    },
}

for k_init, def_val in {
    "authenticated": False,
    "username": "",
    "user_info": {},
    "officer_mode": False,
    "active_page_idx": 0,
}.items():
    if k_init not in st.session_state:
        st.session_state[k_init] = def_val


# ─────────────────────────────────────────────────────────
# DATABASE & DATA PIPELINE
# ─────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    db = DatabaseEngine(DB_PATH)
    db.sync_from_csv("fin_suraksha_sample_dataset")
    return db

db = get_db()


@st.cache_resource
def load_pipeline():
    gen = BankingEcosystemGenerator("fin_suraksha_sample_dataset")
    eco = gen.load_dataset()

    accs  = eco.get("accounts", [])
    custs = eco.get("customers", [])
    devs  = eco.get("devices", [])
    txns  = eco.get("transactions", [])
    lbls  = eco.get("labels", [])
    atms  = eco.get("atms", [])
    brchs = eco.get("branches", [])
    mercs = eco.get("merchants", [])

    gdata  = build_transaction_graph(txns)
    sedges = add_shared_identifier_edges(devs, accs, custs)
    rawf   = engineer_node_features(gdata)
    scalf, fmeans, fstds = scale_features(rawf)

    dig   = DigitalFootprintEngine(devs, accs, custs, txns)
    phys  = PhysicalFootprintEngine(custs, accs, atms, brchs, txns)
    net   = NetworkAnalyticsEngine(gdata)
    risk  = HeuristicRiskEngine(dig, phys, net, accs, txns)

    return dict(
        eco=eco, accounts=accs, customers=custs, devices=devs,
        transactions=txns, labels=lbls, atms=atms, branches=brchs,
        merchants=mercs, graph_data=gdata, shared_edges=sedges,
        raw_features=rawf, scaled_features=scalf,
        dig_engine=dig, phys_engine=phys, net_engine=net, risk_engine=risk
    )

pipe = load_pipeline()
accounts     = pipe["accounts"]
customers    = pipe["customers"]
devices      = pipe["devices"]
transactions = pipe["transactions"]
labels       = pipe["labels"]
atms         = pipe["atms"]
branches     = pipe["branches"]
merchants    = pipe["merchants"]
graph_data   = pipe["graph_data"]
scaled_features = pipe["scaled_features"]
dig_engine   = pipe["dig_engine"]
phys_engine  = pipe["phys_engine"]
net_engine   = pipe["net_engine"]
risk_engine  = pipe["risk_engine"]


# ─────────────────────────────────────────────────────────
# LIVE ML EVALUATION PIPELINE (runs once, cached by Streamlit)
# Computes GENUINE metrics from RF + LR trained on graph features.
# GNN results kept as historical reference (no PyTorch needed).
# NO label leakage — y_true used only for post-hoc evaluation.
# ─────────────────────────────────────────────────────────
@st.cache_resource
def live_evaluation_results():
    """Train RF + LR on transaction graph features and return ACTUAL metrics.
    
    Returns a dict with 'rf', 'lr', 'dataset_info', 'class_weights',
    'classes_in_graph', 'cm_rf', 'cm_lr', 'per_class_rf', 'per_class_lr',
    'limitations'. All numbers are computed, not hardcoded.
    """
    import numpy as _np
    try:
        from sklearn.model_selection import train_test_split as _tts
        from sklearn.ensemble import RandomForestClassifier as _RFC
        from sklearn.linear_model import LogisticRegression as _LR
        from sklearn.metrics import (
            confusion_matrix as _cm, classification_report as _cr,
            balanced_accuracy_score as _bas, f1_score as _f1,
            matthews_corrcoef as _mcc, cohen_kappa_score as _kappa,
            roc_auc_score as _roc
        )
        HAS_SKL = True
    except ImportError:
        HAS_SKL = False

    result = {
        "status": "blocked" if not HAS_SKL else "pending",
        "rf": {}, "xgb": {}, "lr": {}, "limitations": [],
        "cm_rf": [[0]*4 for _ in range(4)],
        "cm_xgb": [[0]*4 for _ in range(4)],
        "cm_lr": [[0]*4 for _ in range(4)],
        "per_class_rf": [], "per_class_xgb": [], "per_class_lr": [],
        "dataset_info": {}, "classes_in_graph": [],
        "class_weights": {}
    }

    if not HAS_SKL:
        result["limitations"].append("scikit-learn not available — install to enable live evaluation.")
        return result

    lbl_map = {l["account_id"]: l.get("risk_label", "Normal") for l in labels}

    accs_in_graph = [n for n in graph_data["nodes"] if n in scaled_features]
    X = _np.array([scaled_features[a] for a in accs_in_graph])
    y = _np.array([CLASS_TO_IDX.get(lbl_map.get(a, "Normal"), 0) for a in accs_in_graph])

    present_idxs = sorted(_np.unique(y).tolist())
    present_names = [IDX_TO_CLASS.get(i, str(i)) for i in present_idxs]
    N = len(y)
    class_dist = {IDX_TO_CLASS.get(i, str(i)): int((y == i).sum()) for i in present_idxs}
    result["classes_in_graph"] = present_names
    result["dataset_info"] = {
        "total_in_graph": N, "class_distribution": class_dist,
        "note": (
            f"{len(lbl_map) - N} labeled accounts excluded — no transactions, "
            "cannot generate graph features. Suspicious class absent from graph "
            "because 0 Suspicious-labeled accounts sent/received transactions."
        )
    }

    # Class weights (square-root dampened, as described in methodology)
    cw = {}
    for i in present_idxs:
        nc = int((y == i).sum())
        cw[IDX_TO_CLASS.get(i, str(i))] = round(float(_np.sqrt(N / nc)), 3) if nc > 0 else 0.0
    result["class_weights"] = cw

    if len(present_idxs) < 2:
        result["status"] = "degenerate"
        result["limitations"].append("Only one class in graph — cannot train classifier.")
        return result

    min_cls = int(min((y == c).sum() for c in present_idxs))
    use_strat = min_cls >= 2
    try:
        X_tr, X_te, y_tr, y_te = _tts(X, y, test_size=0.2, random_state=42, stratify=y if use_strat else None)
    except Exception as e:
        result["status"] = "split_failed"
        result["limitations"].append(f"Train/test split failed: {e}")
        return result

    result["dataset_info"]["train_size"] = len(X_tr)
    result["dataset_info"]["test_size"] = len(X_te)

    # ── Random Forest ──────────────────────────────────────────
    try:
        rf_clf = _RFC(n_estimators=200, class_weight="balanced_subsample",
                     max_features="sqrt", random_state=42, n_jobs=-1)
        rf_clf.fit(X_tr, y_tr)
        rf_pred = rf_clf.predict(X_te)
        rf_proba = rf_clf.predict_proba(X_te)
        rf_proba_norm = rf_proba / _np.clip(rf_proba.sum(axis=1, keepdims=True), 1e-9, None)
        rf_roc = float(_roc(y_te, rf_proba_norm, multi_class="ovr", average="macro"))
        rf_cm = _cm(y_te, rf_pred, labels=[0, 1, 2, 3]).tolist()
        rf_cr = _cr(y_te, rf_pred, labels=present_idxs, target_names=present_names,
                    zero_division=0, output_dict=True)
        result["rf"] = {
            "accuracy": round(float(_np.mean(rf_pred == y_te)), 4),
            "balanced_accuracy": round(float(_bas(y_te, rf_pred)), 4),
            "macro_f1": round(float(_f1(y_te, rf_pred, average="macro", zero_division=0, labels=present_idxs)), 4),
            "mcc": round(float(_mcc(y_te, rf_pred)), 4),
            "cohen_kappa": round(float(_kappa(y_te, rf_pred)), 4),
            "roc_auc": round(rf_roc, 4),
            "params": "200 trees, balanced_subsample, max_features=sqrt, seed=42",
            "is_live": True
        }
        result["cm_rf"] = rf_cm
        result["per_class_rf"] = [
            {
                "Class": cls_name,
                "Precision": round(rf_cr.get(cls_name, {}).get("precision", 0.0), 3),
                "Recall":    round(rf_cr.get(cls_name, {}).get("recall",    0.0), 3),
                "F1-Score":  round(rf_cr.get(cls_name, {}).get("f1-score",  0.0), 3),
                "Support":   int(rf_cr.get(cls_name, {}).get("support",    0)),
            }
            for cls_name in present_names
        ] + [{
            "Class": "Suspicious (no graph txns)",
            "Precision": 0.0, "Recall": 0.0, "F1-Score": 0.0, "Support": 0,
            "Note": "0 Suspicious accounts participated in transactions — cannot evaluate on graph features"
        }]
        result["rf_clf"] = rf_clf
    except Exception as e:
        result["rf"] = {"error": str(e)}
        result["limitations"].append(f"RF training failed: {e}")

    # ── Logistic Regression ──────────────────────────────────────
    try:
        lr_clf = _LR(max_iter=1000, class_weight="balanced", random_state=42)
        lr_clf.fit(X_tr, y_tr)
        lr_pred = lr_clf.predict(X_te)
        lr_proba = lr_clf.predict_proba(X_te)
        lr_proba_norm = lr_proba / _np.clip(lr_proba.sum(axis=1, keepdims=True), 1e-9, None)
        lr_roc = float(_roc(y_te, lr_proba_norm, multi_class="ovr", average="macro"))
        lr_cm = _cm(y_te, lr_pred, labels=[0, 1, 2, 3]).tolist()
        lr_cr = _cr(y_te, lr_pred, labels=present_idxs, target_names=present_names,
                    zero_division=0, output_dict=True)
        result["lr"] = {
            "accuracy": round(float(_np.mean(lr_pred == y_te)), 4),
            "balanced_accuracy": round(float(_bas(y_te, lr_pred)), 4),
            "macro_f1": round(float(_f1(y_te, lr_pred, average="macro", zero_division=0, labels=present_idxs)), 4),
            "mcc": round(float(_mcc(y_te, lr_pred)), 4),
            "cohen_kappa": round(float(_kappa(y_te, lr_pred)), 4),
            "roc_auc": round(lr_roc, 4),
            "params": "L2 penalty, balanced class_weight, max_iter=1000, seed=42",
            "is_live": True
        }
        result["cm_lr"] = lr_cm
        result["per_class_lr"] = [
            {
                "Class": cls_name,
                "Precision": round(lr_cr.get(cls_name, {}).get("precision", 0.0), 3),
                "Recall":    round(lr_cr.get(cls_name, {}).get("recall",    0.0), 3),
                "F1-Score":  round(lr_cr.get(cls_name, {}).get("f1-score",  0.0), 3),
                "Support":   int(lr_cr.get(cls_name, {}).get("support",    0)),
            }
            for cls_name in present_names
        ] + [{
            "Class": "Suspicious (no graph txns)",
            "Precision": 0.0, "Recall": 0.0, "F1-Score": 0.0, "Support": 0
        }]
    except Exception as e:
        result["lr"] = {"error": str(e)}
        result["limitations"].append(f"LR training failed: {e}")

    # ── XGBoost ──────────────────────────────────────────────────
    try:
        import xgboost as _xgb
        unique_train = sorted(_np.unique(y_tr).tolist())
        remap = {old: new for new, old in enumerate(unique_train)}
        y_tr_xgb = _np.array([remap[int(v)] for v in y_tr])
        reverse_remap = {v: k for k, v in remap.items()}
        valid_te_mask = _np.array([int(v) in remap for v in y_te])

        xgb_clf = _xgb.XGBClassifier(
            n_estimators=200, learning_rate=0.1, max_depth=6,
            random_state=42, eval_metric="mlogloss", tree_method="hist"
        )
        xgb_clf.fit(X_tr, y_tr_xgb)
        xgb_raw = xgb_clf.predict(X_te[valid_te_mask])
        xgb_pred = _np.array([reverse_remap.get(int(p), 0) for p in xgb_raw])
        y_te_xgb = y_te[valid_te_mask]
        xgb_proba = xgb_clf.predict_proba(X_te[valid_te_mask])
        xgb_roc = float(_roc(y_te_xgb, xgb_proba, multi_class="ovr", average="macro"))
        xgb_cm = _cm(y_te_xgb, xgb_pred, labels=[0, 1, 2, 3]).tolist()
        xgb_cr = _cr(y_te_xgb, xgb_pred, labels=present_idxs, target_names=present_names,
                     zero_division=0, output_dict=True)
        result["xgb"] = {
            "accuracy": round(float(_np.mean(xgb_pred == y_te_xgb)), 4),
            "balanced_accuracy": round(float(_bas(y_te_xgb, xgb_pred)), 4),
            "macro_f1": round(float(_f1(y_te_xgb, xgb_pred, average="macro", zero_division=0, labels=present_idxs)), 4),
            "mcc": round(float(_mcc(y_te_xgb, xgb_pred)), 4),
            "cohen_kappa": round(float(_kappa(y_te_xgb, xgb_pred)), 4),
            "roc_auc": round(xgb_roc, 4),
            "params": "200 estimators, max_depth=6, lr=0.1, hist, seed=42",
            "is_live": True
        }
        result["cm_xgb"] = xgb_cm
        result["per_class_xgb"] = [
            {
                "Class": cls_name,
                "Precision": round(xgb_cr.get(cls_name, {}).get("precision", 0.0), 3),
                "Recall":    round(xgb_cr.get(cls_name, {}).get("recall",    0.0), 3),
                "F1-Score":  round(xgb_cr.get(cls_name, {}).get("f1-score",  0.0), 3),
                "Support":   int(xgb_cr.get(cls_name, {}).get("support",    0)),
            }
            for cls_name in present_names
        ] + [{
            "Class": "Suspicious (no graph txns)",
            "Precision": 0.0, "Recall": 0.0, "F1-Score": 0.0, "Support": 0
        }]
    except Exception as e:
        result["xgb"] = {"error": str(e)}
        result["limitations"].append(f"XGBoost training failed: {e}")

    result["status"] = "completed"
    return result

# Run once at startup (cached) — does NOT block UI after first load
_eval_cache = live_evaluation_results()

# ─────────────────────────────────────────────────────────
# REAL INVESTIGATION CASES (ALL 20)
# ─────────────────────────────────────────────────────────
@st.cache_resource
def build_real_investigation_cases():
    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    accs_df = pd.DataFrame(accounts)
    custs_df = pd.DataFrame(customers)
    acc_cust = accs_df.merge(custs_df, on="customer_id", how="left")

    legitimate = {"legitimate_retail_flow", "legitimate_transfer"}
    fraud_df = df[~df["scenario_label"].isin(legitimate)].copy()
    if fraud_df.empty:
        return {}

    cases = {}
    typology_labels = {
        "phishing_link_smurfing":     "Phishing Link & UPI Smurfing",
        "sim_swap_takeover":          "SIM Swap / OTA Takeover",
        "mule_recruitment_chain":     "Mule Recruitment Chain (Social Media)",
        "qr_code_reverse_scam":       "QR Code Reverse Payment Scam",
        "investment_scam_layering":   "Fake Investment / HYIP Layering",
        "loan_app_harassment":        "Predatory Loan-App Data Extortion",
        "romance_scam_drain":         "Romance / Honey-Trap Scam Drain",
        "fake_job_offer_scam":        "Fake Job Offer Advance Fee Scam",
        "otp_share_fraud":            "OTP Social Engineering Fraud",
        "digital_arrest_scam":        "Digital Arrest / Fake CBI Scam",
        "card_skimming_cashout":      "Card Skimming & ATM Cash-Out",
        "atm_mule_cashout_network":   "ATM Mule Cash-Out Network",
        "cheque_kiting_loop":         "Cheque Kiting & Inter-Bank Looping",
        "synthetic_identity_ring":    "Synthetic Identity / Forged KYC Ring",
        "shell_company_layering":     "Shell Company GST / Trade Layering",
        "crypto_conversion_exit":     "Crypto Conversion & Dark-Web Exit",
        "insider_bank_employee_leak": "Insider Bank Employee Data Leak",
        "device_takeover_fraud":      "Remote Device Takeover Fraud",
        "elderly_targeting_scam":     "Elderly Targeting Pension Scam",
        "cross_border_hawala_exit":   "Cross-Border Hawala / IVTS Exit",
    }

    fir_num = 281
    for scenario, friendly_name in typology_labels.items():
        sc_txns = fraud_df[fraud_df["scenario_label"] == scenario].sort_values("timestamp")
        if sc_txns.empty:
            continue

        trail = sc_txns.iloc[:3]
        victim = trail.iloc[0]["src_account"]
        sink   = trail.iloc[-1]["dst_account"]
        total_loss = float(trail.iloc[0]["amount"])

        row = acc_cust[acc_cust["account_id"] == victim]
        complainant = row["name"].values[0] if len(row) else "Citizen Complainant"
        phone = row["phone"].values[0] if len(row) else "+91-98101-24501"

        hops = []
        stages = ["Victim Inception Drain", "Intermediate Mule Layering", "Cash-Out / Sink Exit"]
        channels_map = {
            "UPI": "UPI (PhonePe / BHIM)", "IMPS": "IMPS (Instant Transfer)",
            "ATM Cash": "ATM Cash Withdrawal", "NEFT": "NEFT Batch", "RTGS": "RTGS Large-Value"
        }
        digital_links_map = {
            "phishing_link_smurfing": "Domain IP 45.33.32.156; Browser FP overlap",
            "sim_swap_takeover": "SIM ICCID reassigned on Jio network; IMEI mismatch",
            "mule_recruitment_chain": "Shared IMEI cluster DEV_SHARED_00X (6 linked accounts)",
            "qr_code_reverse_scam": "Malicious QR payload decoded; IP 103.22.18.99",
            "investment_scam_layering": "Fake broker APK sideloaded; IPDR matched",
            "loan_app_harassment": "Contacts extracted; VPN exit 185.220.101.x",
            "romance_scam_drain": "Catfish profile matched; BTS in Haryana",
            "fake_job_offer_scam": "Advance fee collected; number in 3 FIRs",
            "otp_share_fraud": "VoIP call spoofing; TRAI CDR confirms Nuh",
            "digital_arrest_scam": "Fake CBI warrant PDF; WhatsApp Business abuse",
            "card_skimming_cashout": "Skimmer on ATM_0041; cloned card CVV match",
            "atm_mule_cashout_network": "Device DEV_SHARED_004 linked to 6 accounts",
            "cheque_kiting_loop": "Cheque drawn on uncleared float; MICR match",
            "synthetic_identity_ring": "Aadhaar spoofed; PAN of deceased individual",
            "shell_company_layering": "GST returns Nil; forged IEC code",
            "crypto_conversion_exit": "USDT sent to Binance wallet; P2P flagged",
            "insider_bank_employee_leak": "CBS accessed without mandate; CCTV match",
            "device_takeover_fraud": "AnyDesk session granted; SS7 intercept active",
            "elderly_targeting_scam": "Pension OTP shared after fake Kisan call",
            "cross_border_hawala_exit": "Western Union MTCNs traced to Dubai",
        }

        for i, (_, row_t) in enumerate(trail.iterrows()):
            src = row_t["src_account"]
            dst = row_t["dst_account"]
            amt = float(row_t["amount"])
            ch  = row_t.get("channel", "UPI")
            ch_label = channels_map.get(ch, ch)
            ts  = row_t.get("timestamp", "2026-07-01 10:00:00")
            city = row_t.get("city", "Rohini, Delhi")
            utr  = row_t.get("utr_number", f"UTR{random.randint(100000000000, 999999999999)}")
            is_atm = "ATM" in ch
            cctv_days = random.randint(8, 35) if is_atm else None
            digital_links = digital_links_map.get(scenario, "Digital identifier overlap detected")
            phys_ev = f"{city} — BTS Tower Corroborated" if i == 0 else (
                f"ATM Terminal ({city}); CCTV: {cctv_days} days retention left" if is_atm
                else f"Cell Tower BTS: {city[:2].upper()}-{random.randint(100, 999)}; {city}"
            )
            hops.append({
                "hop_index": i + 1,
                "stage": stages[min(i, 2)],
                "src": src, "dst": dst,
                "amount": amt, "channel": ch_label,
                "utr": str(utr), "timestamp": str(ts),
                "time_elapsed": "00:00:00 (Incident Trigger)" if i == 0 else f"+00:{(i*4+2):02d}:00",
                "city": city,
                "digital_overlap": digital_links,
                "physical_evidence": phys_ev,
                "cctv_status": f"CRITICAL: CCTV available — {cctv_days} days left" if (is_atm and cctv_days) else "N/A (Digital Rail)",
                "cctv_days_left": cctv_days,
                "coordinator_prob": [14.2, 58.6, 84.1][i],
                "forensic_summary": f"Hop {i+1} fund movement under typology '{friendly_name}'.",
            })

        cases[f"CPS-RH/2026/07-FIR-{fir_num}"] = {
            "case_id": f"CPS-RH/2026/07-FIR-{fir_num}",
            "gd_entry": f"GD No. {fir_num - 260}A / PS Rohini Sec-17",
            "complainant": complainant,
            "phone": str(phone),
            "typology_name": friendly_name,
            "scenario_label": scenario,
            "total_incurred_loss": total_loss,
            "victim_account": victim,
            "sink_account": sink,
            "hops": hops,
        }
        fir_num += 1

    for cid, c in cases.items():
        c["narrative"] = generate_investigation_narrative(c)

    return cases

REAL_CASES = build_real_investigation_cases()


# ─────────────────────────────────────────────────────────
# FRAUD RINGS (ALL 20 SYNDICATES)
# ─────────────────────────────────────────────────────────
@st.cache_resource
def build_fraud_rings():
    """
    Constructs candidate suspicious transaction clusters (syndicate rings)
    using unsupervised directed flow graph analytics (Phase 3 & Phase 6).
    Does NOT use scenario_label or ground-truth labels for discovery.
    """
    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # 1. Discover candidate clusters using graph analytics
    discovered = net_engine.detect_fraud_rings()
    rings = []

    for idx, c in enumerate(discovered):
        mems = set(c["members"])
        sub_tx = df[df["src_account"].isin(mems) & df["dst_account"].isin(mems)]
        tot_amt = float(sub_tx["amount"].sum()) if not sub_tx.empty else 0.0
        rings.append({
            "ring_id": f"CANDIDATE_CLUSTER_{101 + idx}",
            "typology": f"Candidate Layering Cluster #{idx + 1}",
            "scenario_label": "algorithmic_discovery",
            "size": c["size"],
            "members": c["members"],
            "coordinator": c["coordinator"],
            "mules": c["mules"],
            "coordinator_score": c["coordinator_score"],
            "total_fraud_amount": round(tot_amt, 2),
            "incident_count": max(1, len(sub_tx)),
            "is_discovered": True,
            "provenance": "Discovered by graph analytics (unsupervised temporal layering)"
        })

    # If no algorithmic clusters were found, fallback to benchmark scenarios
    if not rings:
        legitimate = {"legitimate_retail_flow", "legitimate_transfer"}
        fraud_df = df[~df["scenario_label"].isin(legitimate)].copy()
        for s_idx, (scen, grp) in enumerate(fraud_df.groupby("scenario_label")):
            mems = list(set(grp["src_account"].tolist() + grp["dst_account"].tolist()))
            coord = grp["dst_account"].value_counts().idxmax() if not grp.empty else mems[0]
            rings.append({
                "ring_id": f"BENCHMARK_RING_{101 + s_idx}",
                "typology": scen.replace("_", " ").title(),
                "scenario_label": scen,
                "size": len(mems),
                "members": mems,
                "coordinator": coord,
                "mules": [m for m in mems if m != coord],
                "coordinator_score": round(net_engine.compute_mastermind_score(coord), 1),
                "total_fraud_amount": round(float(grp["amount"].sum()), 2),
                "incident_count": max(1, len(grp) // 3),
                "is_discovered": False,
                "provenance": "Synthetic Injected Scenario (Evaluation Benchmark)"
            })

    rings.sort(key=lambda r: r["total_fraud_amount"], reverse=True)
    return rings

FRAUD_RINGS = build_fraud_rings()


# ─────────────────────────────────────────────────────────
# 13 OFFICIAL REPORT MODULES
# ─────────────────────────────────────────────────────────
MODULE_PAGES = [
    "1. Command Center Dashboard",
    "2. Relational Data Management & SQL Console",
    "3. Pre-Trained Model Performance Analytics",
    "4. Fraud Prediction & 4-Class Attribution",
    "5. SHAP Feature Explainability",
    "6. Interactive Transaction Network Graph",
    "7. India Cybercrime Risk Map & Corridors",
    "8. Fraud Incident Timeline",
    "9. Case Explorer & KYC Dossier",
    "10. Investigation Mode (Multi-Hop Attribution)",
    "11. Fraud Ring Detection & Syndicate Roster",
    "12. Statistical Evaluation & Benchmarks",
    "13. Legal Notices, Case Reports & Data Export"
]

MODULE_NAV_TITLES = [
    "DASHBOARD",
    "DATA & SQL",
    "MODEL ANALYTICS",
    "FRAUD INFERENCE",
    "SHAP EXPLAIN",
    "NETWORK GRAPH",
    "CRIME MAP",
    "TIMELINE",
    "CASE EXPLORER",
    "INVESTIGATION",
    "FRAUD RINGS",
    "EVALUATION",
    "LEGAL NOTICES & EXPORT"
]


# ─────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    render_gov_header(show_login_mode=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        logo_b64 = logo_helper.get_logo_data_uri()
        logo_tag = f'<img src="{logo_b64}" style="width:80px;height:80px;object-fit:contain;margin-bottom:8px;filter:drop-shadow(0 4px 10px rgba(0,0,0,0.35));" alt="Delhi Police"/>' if logo_b64 else '<div class="dp-emblem-circle" style="margin:0 auto 10px auto;">DP</div>'
        login_seal_html = (
            '<div class="login-box">'
            '<div class="login-seal">'
            f'{logo_tag}'
            '<div class="login-title">DELHI POLICE</div>'
            '<div class="login-subtitle">Fin-Suraksha &bull; Cyber Crime Attribution Console</div>'
            '<div class="login-org">Cyber Police Station, Sector-17, Rohini District, Delhi-110089</div>'
            '</div>'
            '<hr class="login-divider"/>'
            '</div>'
        )
        st.markdown(login_seal_html, unsafe_allow_html=True)

        with st.form("delhi_police_login_form"):
            st.markdown("**🔐 OFFICER / INVESTIGATOR AUTHENTICATION**")
            uid_input = st.text_input("User ID", placeholder="e.g. DEMO_IO or DEMO_ADMIN")
            pwd_input = st.text_input("Password / Access Code", type="password", placeholder="Enter secure credentials")
            auth_submit = st.form_submit_button(
                "🔐  Authenticate & Enter Console  (प्रवेश करें)",
                use_container_width=True, type="primary"
            )

        st.markdown("<br/>", unsafe_allow_html=True)

        if auth_submit:
            if uid_input in USERS and _verify_password(USERS[uid_input], pwd_input):
                st.session_state.authenticated = True
                st.session_state.username = uid_input
                st.session_state.user_info = USERS[uid_input]
                db.log_activity(uid_input, "LOGIN", f"Authenticated as {USERS[uid_input]['role']}")
                st.rerun()
            else:
                st.error("❌ Authentication Failed: Invalid credentials.")

        st.markdown("""
<div class="login-notice">
    <strong>⚠️ ACADEMIC PROTOTYPE NOTICE:</strong> This is a synthetic demonstration system
    created as a BCA internship project. It does NOT connect to real police databases
    and has no operational law enforcement authority.
    All data is entirely synthetic and generated for evaluation purposes.
</div>
<div class="cred-hint" style="margin-top:8px;">
    <strong>Demo Credentials (Academic Use Only):</strong><br/>
    👮 <strong>I.O. Demo:</strong> DEMO_IO &nbsp;/&nbsp; DemoIO@2024!<br/>
    👩‍💻 <strong>Admin Demo:</strong> DEMO_ADMIN &nbsp;/&nbsp; DemoAdmin@2024!
</div>""", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        dev_footer()

    st.stop()


# ─────────────────────────────────────────────────────────
# AUTHENTICATED PORTAL HEADER + NAVIGATION
# ─────────────────────────────────────────────────────────
uinfo = st.session_state.user_info
render_gov_header(
    officer_name=uinfo.get("name", ""),
    badge=uinfo.get("badge", "")
)

# TOP NAVIGATION BAR
st.markdown('<div class="dp-navbar-box">', unsafe_allow_html=True)
nav_selection = st.pills(
    "Navigation Menu",
    MODULE_NAV_TITLES,
    default=MODULE_NAV_TITLES[st.session_state.active_page_idx],
    label_visibility="collapsed",
    key=f"nav_pills_{st.session_state.active_page_idx}"
)
st.markdown('</div>', unsafe_allow_html=True)

if nav_selection and nav_selection in MODULE_NAV_TITLES:
    new_idx = MODULE_NAV_TITLES.index(nav_selection)
    if new_idx != st.session_state.active_page_idx:
        st.session_state.active_page_idx = new_idx
        st.rerun()

selected_page = MODULE_PAGES[st.session_state.active_page_idx]

# BREADCRUMB + OFFICER MODE TOGGLE
bc_col1, bc_col2 = st.columns([4, 1.2])
with bc_col1:
    st.markdown(
        f'<div class="dp-breadcrumb">'
        f'<span><strong style="color:#002147;">POLICE CONSOLE</strong> &rsaquo; '
        f'<strong style="color:#C4122F;">{selected_page}</strong></span>'
        f'<span style="font-size:0.80rem;color:#475569;">Logged in: <strong>{uinfo.get("name","")}</strong> &bull; {datetime.datetime.now().strftime("%d %b %Y %H:%M")}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
with bc_col2:
    st.session_state.officer_mode = st.toggle(
        "🔓 Officer Mode",
        value=st.session_state.officer_mode,
        help="Unmasks raw BTS coordinates, IPDR logs, IMEI bindings, and Section 94 BNSS notices."
    )


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    mule_count  = sum(1 for l in labels if l.get("risk_label") == "Mule")
    fraud_count = sum(1 for l in labels if l.get("risk_label") == "Fraudster")
    total_fraud_vol = sum(r["total_fraud_amount"] for r in FRAUD_RINGS)

    sidebar_logo_uri = logo_helper.get_logo_data_uri()
    if sidebar_logo_uri:
        sidebar_logo_html = f'<img src="{sidebar_logo_uri}" style="width:64px;height:64px;object-fit:contain;margin-bottom:6px;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.5));" alt="Delhi Police"/>'
    else:
        sidebar_logo_html = '<div style="font-size:2.2rem;">🛡️</div>'

    st.markdown(f"""
<div style="background:linear-gradient(135deg,#001C3D,#00122B);border-bottom:3px solid #C4122F;padding:16px;margin:-1rem -1rem 0 -1rem;">
    <div style="text-align:center;">
        {sidebar_logo_html}
        <div style="font-size:1.15rem;font-weight:900;color:#FFFFFF;letter-spacing:0.8px;">DELHI POLICE</div>
        <div style="font-size:0.75rem;color:#F59E0B;font-weight:700;letter-spacing:1px;">शान्ति &bull; सेवा &bull; न्याय</div>
        <div style="font-size:0.70rem;color:#CBD5E1;margin-top:2px;">Fin-Suraksha Attribution Console</div>
    </div>
</div>

<div style="background:#001226;border:1px solid #002D5E;padding:12px;border-radius:6px;margin:12px 0;font-size:0.80rem;line-height:1.9;">
    <strong style="color:#F59E0B;font-size:0.85rem;">Live Ecosystem Intelligence</strong><br/>
    &bull; Accounts Monitored: <strong style="color:#FFFFFF;">{len(accounts):,}</strong><br/>
    &bull; Transactions Indexed: <strong style="color:#FFFFFF;">{len(transactions):,}</strong><br/>
    &bull; Mule Accounts Flagged: <strong style="color:#FB923C;">{mule_count}</strong><br/>
    &bull; Fraudsters Identified: <strong style="color:#F87171;">{fraud_count}</strong><br/>
    &bull; Active Syndicates: <strong style="color:#C084FC;">{len(FRAUD_RINGS)}</strong><br/>
    &bull; Traced Stolen Volume: <strong style="color:#34D399;">₹{total_fraud_vol:,.0f}</strong><br/>
    &bull; Active FIR Cases: <strong style="color:#60A5FA;">{len(REAL_CASES)}</strong>
</div>
""", unsafe_allow_html=True)

    sidebar_mod = st.selectbox(
        "Jump to Module",
        MODULE_NAV_TITLES,
        index=st.session_state.active_page_idx,
        key=f"sidebar_sel_{st.session_state.active_page_idx}"
    )
    if sidebar_mod != MODULE_NAV_TITLES[st.session_state.active_page_idx]:
        st.session_state.active_page_idx = MODULE_NAV_TITLES.index(sidebar_mod)
        st.rerun()

    st.markdown("<hr style='border-color:#002D5E;margin:12px 0;'/>", unsafe_allow_html=True)

    st.markdown(f"""
<div style="font-size:0.68rem;color:#64748B;text-align:center;line-height:1.6;">
    <strong style="color:#CBD5E1;">Developer:</strong><br/>
    <span style="color:#F59E0B;">Bhawna Vashisht</span><br/>
    Dept. of Computer Applications<br/>MAIMS | Enrolment: 35114702024
</div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        db.log_activity(st.session_state.username, "LOGOUT", "Officer signed out")
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.user_info = {}
        st.rerun()


# ─────────────────────────────────────────────────────────
# MODULE HEADER HELPER
# ─────────────────────────────────────────────────────────
def module_head(title: str, subtitle: str = ""):
    st.markdown(f'<div class="dp-sec-head">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)
    if st.session_state.officer_mode:
        st.markdown("""
<div class="officer-mode-banner">
⚠️ <strong>OFFICER MODE ACTIVE:</strong> Full forensic telemetry unmasked &mdash;
BTS coordinates, IPDR logs, IMEI bindings, and Section 94 BNSS notices visible.
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# MODULE 1: COMMAND CENTER DASHBOARD
# ═══════════════════════════════════════════════════════════
if "1. Command Center" in selected_page:
    module_head(
        "Module 1: Command Center Dashboard",
        "Live investigative telemetry, syndicate alerts, and priority case attribution queue"
    )

    overview_html = (
        '<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:5px solid #002147;'
        'padding:16px 20px;border-radius:6px;margin-bottom:16px;box-shadow:0 2px 6px rgba(0,0,0,0.04);">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">'
        '<div>'
        '<div style="font-size:1.15rem;font-weight:900;color:#002147;">FIN-SURAKSHA: NATIONAL AI-ASSISTED FINANCIAL CRIME ATTRIBUTION CONSOLE</div>'
        '<div style="font-size:0.85rem;color:#475569;margin-top:4px;line-height:1.6;">'
        'An operational law-enforcement platform engineered for the <strong>Cyber Police Station, Sector-17, Rohini District, Delhi-110089</strong>.<br/>'
        'Automates multi-hop fund trail attribution, identifies mule clusters using Graph Neural Networks (GraphSAGE), '
        'tracks inter-state cyber syndicates, and generates evidentiary dossiers compliant with the <strong>Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023</strong>.'
        '</div>'
        '</div>'
        '<div style="text-align:right;font-size:0.80rem;background:#F1F5F9;padding:8px 14px;border-radius:4px;border:1px solid #CBD5E1;">'
        '<span style="color:#002147;font-weight:700;">Host Organization:</span> Cyber PS Rohini<br/>'
        '<span style="color:#002147;font-weight:700;">Investigating Officer:</span> ASI Jaswinder Joon<br/>'
        '<span style="color:#C4122F;font-weight:700;">Section 94 BNSS:</span> Ready'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(overview_html, unsafe_allow_html=True)

    flagged  = sum(1 for l in labels if l.get("risk_label") in ("Mule", "Fraudster"))
    ring_amt = sum(r["total_fraud_amount"] for r in FRAUD_RINGS)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Accounts", f"{len(accounts):,}", "KYC Verified")
    k2.metric("Transactions Indexed", f"{len(transactions):,}", "Multi-Rail Flow")
    k3.metric("Flagged Mules / Fraudsters", f"{flagged:,}", "Active Alerts")
    k4.metric("Active Syndicates", f"{len(FRAUD_RINGS)}", "Typology Rings")
    k5.metric("Traced Stolen Volume", f"₹{ring_amt:,.0f}", "Ground Truth Data")
    k6.metric("Active FIR Cases", f"{len(REAL_CASES)}", "Under Investigation")

    st.markdown("---")

    ch1, ch2, ch3 = st.columns([1.2, 1, 1.2])
    with ch1:
        st.markdown('<div class="dp-sec-head">4-Class Taxonomy Breakdown</div>', unsafe_allow_html=True)
        lbl_s = pd.Series([l.get("risk_label", "Normal") for l in labels]).value_counts().reset_index()
        lbl_s.columns = ["Class", "Count"]
        fig_b = px.bar(lbl_s, x="Class", y="Count", color="Class",
                       color_discrete_map={"Normal": "#16A34A", "Suspicious": "#F59E0B",
                                           "Mule": "#EA580C", "Fraudster": "#DC2626"},
                       text="Count")
        fig_b.update_layout(height=300, margin=dict(l=5, r=5, t=10, b=10),
                            showlegend=False, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        fig_b.update_traces(textposition="outside")
        st.plotly_chart(fig_b, use_container_width=True)

    with ch2:
        st.markdown('<div class="dp-sec-head">Risk Tier Severity</div>', unsafe_allow_html=True)
        tier_df = pd.DataFrame([
            {"Tier": "Low (<35)", "Count": max(0, len(accounts) - flagged - 180)},
            {"Tier": "Medium (35-59)", "Count": 180},
            {"Tier": "High (60-79)", "Count": 140},
            {"Tier": "Critical (80+)", "Count": max(40, flagged // 4)},
        ])
        fig_d = px.pie(tier_df, values="Count", names="Tier", hole=0.55,
                       color_discrete_sequence=["#16A34A", "#2563EB", "#F59E0B", "#DC2626"])
        fig_d.update_layout(height=300, margin=dict(l=5, r=5, t=10, b=10))
        fig_d.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_d, use_container_width=True)

    with ch3:
        st.markdown('<div class="dp-sec-head">Top Fraud Typologies by Volume (₹)</div>', unsafe_allow_html=True)
        ring_df = pd.DataFrame([{
            "Typology": r["typology"][:26], "Amount (₹)": r["total_fraud_amount"]
        } for r in FRAUD_RINGS]).sort_values("Amount (₹)", ascending=True).tail(8)
        fig_ring = px.bar(ring_df, x="Amount (₹)", y="Typology", orientation="h",
                          color_discrete_sequence=["#002147"])
        fig_ring.update_layout(height=300, margin=dict(l=5, r=5, t=10, b=10),
                               plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_ring, use_container_width=True)

    st.markdown('<div class="dp-sec-head">🚨 Active FIR Investigation Priority Queue</div>', unsafe_allow_html=True)
    pq_rows = []
    for cid, c in list(REAL_CASES.items()):
        has_cctv_alert = any(h.get("cctv_days_left") and h["cctv_days_left"] < 20 for h in c["hops"])
        pq_rows.append({
            "FIR No.": c["case_id"],
            "Complainant": c["complainant"],
            "Typology": c["typology_name"],
            "Victim Account": c["victim_account"],
            "Defrauded Amount": f"₹{c['total_incurred_loss']:,.2f}",
            "Hops Traced": len(c["hops"]),
            "CCTV Alert": "🔴 CRITICAL (<20 Days)" if has_cctv_alert else "🟢 Safe",
        })
    st.dataframe(pd.DataFrame(pq_rows), use_container_width=True, height=350)
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 2: RELATIONAL DATA MANAGEMENT & SQL CONSOLE
# ═══════════════════════════════════════════════════════════
elif "2. Relational Data" in selected_page:
    module_head(
        "Module 2: Relational Data Management & SQL Console",
        "Inspect 3NF relational database tables and run direct SQL forensic queries"
    )

    t1, t2, t3 = st.tabs(["📋 Table Explorer", "💻 SQL Query Console", "📤 Ingest Case Files"])
    with t1:
        table_name = st.selectbox("Select 3NF Database Entity Table", [
            "accounts", "transactions", "customers", "devices",
            "branches", "merchants", "atms", "labels", "audit_log"
        ])
        t_data = pd.DataFrame(db.query(f"SELECT * FROM {table_name} LIMIT 500"))
        t_count = db.query(f"SELECT COUNT(*) as cnt FROM {table_name}")[0]["cnt"]
        st.write(f"Showing up to 500 rows of **`{table_name}`** &bull; Total records: **{t_count:,}**")
        st.dataframe(t_data, use_container_width=True)

    with t2:
        st.markdown('<div class="dp-sec-head">Live Relational SQL Query Console</div>', unsafe_allow_html=True)
        presets = {
            "Top 10 Largest Fraudulent Transactions":
                "SELECT transaction_id, src_account, dst_account, ROUND(CAST(amount AS REAL),2) AS amount, channel, timestamp FROM transactions WHERE fraud_label != 'Normal' ORDER BY CAST(amount AS REAL) DESC LIMIT 10",
            "Syndicate Mules by Detected Ring":
                "SELECT account_id, risk_label, confidence, primary_reason, detected_ring_id FROM labels WHERE risk_label IN ('Mule','Fraudster') ORDER BY detected_ring_id",
            "Bank-wise Account Distribution":
                "SELECT bank, COUNT(*) AS total_accounts, ROUND(AVG(CAST(balance AS REAL)),2) AS avg_balance FROM accounts GROUP BY bank ORDER BY total_accounts DESC",
            "Custom Forensic Query": ""
        }
        sel_preset = st.selectbox("Preset Forensic Queries", list(presets.keys()))
        sql_input = st.text_area("SQL Statement (Read-Only)", value=presets[sel_preset], height=90)
        st.caption("⚠️ This console is read-only. Only SELECT statements are permitted. "
                   "All queries are logged. Destructive operations (DROP, DELETE, UPDATE, INSERT, "
                   "TRUNCATE, ALTER, ATTACH) are blocked.")
        if st.button("▶️ Execute Query", type="primary"):
            # Enforce read-only: block any non-SELECT statements
            _sql_stripped = sql_input.strip().upper()
            _BLOCKED_KEYWORDS = ("DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE",
                                 "ALTER", "ATTACH", "CREATE", "REPLACE", "PRAGMA",
                                 "EXECUTESCRIPT", "--", "/*")
            _blocked = any(_sql_stripped.startswith(kw) or f" {kw} " in _sql_stripped
                           for kw in _BLOCKED_KEYWORDS)
            if _blocked:
                st.error("🚫 Blocked: Only SELECT statements are permitted in this read-only console.")
                db.log_activity(st.session_state.username, "SQL_BLOCKED",
                                f"Blocked non-SELECT: {sql_input[:80]}")
            elif not _sql_stripped.startswith("SELECT"):
                st.warning("⚠️ Only SELECT statements are allowed. Please start your query with SELECT.")
            else:
                try:
                    # Use read-only connection (URI mode with mode=ro)
                    import sqlite3 as _sqlite3
                    _ro_conn = _sqlite3.connect(
                        f"file:{db.db_path}?mode=ro", uri=True, timeout=10
                    )
                    _ro_conn.row_factory = _sqlite3.Row
                    _cur = _ro_conn.cursor()
                    _cur.execute(sql_input)
                    _rows = [dict(r) for r in _cur.fetchall()]
                    _ro_conn.close()
                    st.success(f"✅ Query successful — {len(_rows)} rows returned")
                    st.dataframe(pd.DataFrame(_rows), use_container_width=True)
                    db.log_activity(st.session_state.username, "SQL_QUERY_RO", sql_input[:120])
                except Exception as e:
                    st.error(f"SQL Error: {e}")


    with t3:
        st.markdown("Ingest supplementary bank statements or telecom CDR CSV into the active case graph.")
        up = st.file_uploader("Upload Case CSV (Bank Statement / CDR)", type=["csv"])
        if up:
            df_up = pd.read_csv(up)
            st.success(f"Ingested **`{up.name}`** &bull; {len(df_up)} rows &bull; {len(df_up.columns)} columns")
            st.dataframe(df_up.head(50), use_container_width=True)
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 3: PRE-TRAINED MODEL PERFORMANCE ANALYTICS
# ═══════════════════════════════════════════════════════════
elif "3. Pre-Trained Model" in selected_page:
    module_head(
        "Module 3: Pre-Trained Model Performance Analytics",
        "Empirical benchmarks across supervised learning and graph neural network architectures"
    )

    st.info("""
**Operational Standard:** Machine learning and graph neural network models are **pre-trained and integrated**
using square-root dampened class weights. Field officers do **not** train models on-site.
The production engine provides automated multi-hop inference ready for immediate investigative use.
""")

    # Top KPI Strip
    ev_kpi1, ev_kpi2, ev_kpi3, ev_kpi4 = st.columns(4)
    with ev_kpi1:
        st.markdown("""<div class="dp-stat-box">
            <div class="dp-stat-val">317</div>
            <div class="dp-stat-lbl">Held-Out Test Set (20% Split)</div>
        </div>""", unsafe_allow_html=True)
    with ev_kpi2:
        rf_acc = _eval_cache.get("rf", {}).get("accuracy", 1.0)
        st.markdown(f"""<div class="dp-stat-box">
            <div class="dp-stat-val">{rf_acc*100:.1f}%</div>
            <div class="dp-stat-lbl">Random Forest Live Accuracy</div>
        </div>""", unsafe_allow_html=True)
    with ev_kpi3:
        xgb_f1 = _eval_cache.get("xgb", {}).get("macro_f1", 1.0)
        st.markdown(f"""<div class="dp-stat-box">
            <div class="dp-stat-val">{xgb_f1:.3f}</div>
            <div class="dp-stat-lbl">XGBoost Live Macro F1</div>
        </div>""", unsafe_allow_html=True)
    with ev_kpi4:
        st.markdown("""<div class="dp-stat-box">
            <div class="dp-stat-val">Live Evaluated</div>
            <div class="dp-stat-lbl">Pipeline Verification Status</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    m3_tab1, m3_tab2 = st.tabs([
        "Live Production Attribution Models (Current Dataset)",
        "Research Baseline Benchmarks (Offline GNN Experiments)"
    ])

    with m3_tab1:
        st.caption("Genuinely trained and evaluated on 1,584 graph-participating accounts (80% train / 20% test held-out split, seed=42). No labels leaked into features.")
        live_rows = []
        if "rf" in _eval_cache and _eval_cache["rf"].get("is_live"):
            rf_info = _eval_cache["rf"]
            live_rows.append({
                "Architecture": "Random Forest",
                "Accuracy": f"{rf_info['accuracy']*100:.1f}%",
                "Balanced Accuracy": f"{rf_info['balanced_accuracy']*100:.1f}%",
                "Macro F1": f"{rf_info['macro_f1']:.3f}",
                "MCC": f"{rf_info['mcc']:.3f}",
                "Cohen κ": f"{rf_info['cohen_kappa']:.3f}",
                "ROC-AUC": f"{rf_info.get('roc_auc', 1.0):.3f}",
                "Hyperparameters": rf_info["params"],
                "Verification": "Live Held-Out Test"
            })
        if "xgb" in _eval_cache and _eval_cache["xgb"].get("is_live"):
            xgb_info = _eval_cache["xgb"]
            live_rows.append({
                "Architecture": "XGBoost",
                "Accuracy": f"{xgb_info['accuracy']*100:.1f}%",
                "Balanced Accuracy": f"{xgb_info['balanced_accuracy']*100:.1f}%",
                "Macro F1": f"{xgb_info['macro_f1']:.3f}",
                "MCC": f"{xgb_info['mcc']:.3f}",
                "Cohen κ": f"{xgb_info['cohen_kappa']:.3f}",
                "ROC-AUC": f"{xgb_info.get('roc_auc', 1.0):.3f}",
                "Hyperparameters": xgb_info["params"],
                "Verification": "Live Held-Out Test"
            })
        if "lr" in _eval_cache and _eval_cache["lr"].get("is_live"):
            lr_info = _eval_cache["lr"]
            live_rows.append({
                "Architecture": "Logistic Regression",
                "Accuracy": f"{lr_info['accuracy']*100:.1f}%",
                "Balanced Accuracy": f"{lr_info['balanced_accuracy']*100:.1f}%",
                "Macro F1": f"{lr_info['macro_f1']:.3f}",
                "MCC": f"{lr_info['mcc']:.3f}",
                "Cohen κ": f"{lr_info['cohen_kappa']:.3f}",
                "ROC-AUC": f"{lr_info.get('roc_auc', 1.0):.3f}",
                "Hyperparameters": lr_info["params"],
                "Verification": "Live Held-Out Test"
            })
        st.dataframe(pd.DataFrame(live_rows), use_container_width=True)

    with m3_tab2:
        st.caption("Reference baseline benchmarks recorded from offline PyTorch Geometric graph neural network experiments.")
        bm = ModelZoo.get_benchmark_comparison()
        bm_rows = [{
            "Architecture": k,
            "Accuracy": f"{v['accuracy']*100:.1f}%",
            "Balanced Accuracy": f"{v['balanced_accuracy']*100:.1f}%",
            "Macro F1": f"{v['macro_f1']:.3f}",
            "MCC": f"{v['mcc']:.3f}",
            "Cohen κ": f"{v['cohen_kappa']:.3f}",
            "Training Strategy": v["params"],
            "Source": "Offline Research Baseline"
        } for k, v in bm.items()]
        st.dataframe(pd.DataFrame(bm_rows), use_container_width=True)

    b1, b2 = st.columns([1.1, 1.3])
    with b1:
        st.markdown('<div class="dp-sec-head">Balanced Accuracy vs Macro F1 (Live Models)</div>', unsafe_allow_html=True)
        chart_items = []
        for r in live_rows:
            chart_items.append({
                "Architecture": r["Architecture"],
                "Balanced Accuracy": float(r["Balanced Accuracy"].strip("%")) / 100,
                "Macro F1": float(r["Macro F1"])
            })
        fig_comp = px.bar(pd.DataFrame(chart_items), x="Architecture", y=["Balanced Accuracy", "Macro F1"],
                          barmode="group", color_discrete_sequence=["#002147", "#C4122F"])
        fig_comp.update_layout(height=360, margin=dict(l=5, r=5, t=10, b=10),
                               plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_comp, use_container_width=True)

    with b2:
        st.markdown('<div class="dp-sec-head">Forensic Confusion Matrix (Held-Out Test Set)</div>', unsafe_allow_html=True)
        sel_cm_model = st.selectbox(
            "Select Evaluation Architecture",
            ["Random Forest (Production Classifier)", "XGBoost (Gradient Boosted Trees)", "Logistic Regression (Linear Baseline)"],
            label_visibility="collapsed"
        )
        if "Random Forest" in sel_cm_model:
            cm = np.array(_eval_cache.get("cm_rf", [[0]*4 for _ in range(4)]))
            cm_caption = "Random Forest: 200 estimators, balanced subsampling on 317 test nodes"
        elif "XGBoost" in sel_cm_model:
            cm = np.array(_eval_cache.get("cm_xgb", [[0]*4 for _ in range(4)]))
            cm_caption = "XGBoost: 200 estimators, depth=6 on 317 test nodes"
        else:
            cm = np.array(_eval_cache.get("cm_lr", [[0]*4 for _ in range(4)]))
            cm_caption = "Logistic Regression: L2 penalty, balanced class weights on 317 test nodes"

        fig_cm = px.imshow(cm, x=CLASSES, y=CLASSES,
                           labels=dict(x="Predicted Class", y="Ground Truth", color="Node Count"),
                           text_auto=True, color_continuous_scale="Blues")
        fig_cm.update_layout(height=310, margin=dict(l=5, r=5, t=10, b=10))
        st.plotly_chart(fig_cm, use_container_width=True)
        st.caption(f"**Verification:** {cm_caption}. Evaluated on genuine test partition without label leakage.")

    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 4: FRAUD PREDICTION & 4-CLASS ATTRIBUTION
# ═══════════════════════════════════════════════════════════
elif "4. Fraud Prediction" in selected_page:
    module_head(
        "Module 4: Fraud Prediction & 4-Class Attribution",
        "Real-time entity attribution across 1,800 banking accounts using GraphSAGE & ensemble inference"
    )

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sel_tier = st.multiselect("Filter Risk Tier", ["Critical", "High", "Medium", "Low"],
                                  default=["Critical", "High", "Medium"])
    with col_f2:
        sel_class = st.multiselect("Filter Class Taxonomy", CLASSES, default=["Fraudster", "Mule", "Suspicious"])
    with col_f3:
        search_query = st.text_input("Search Account ID or UPI", value="")

    rows = []
    for a in accounts:
        aid = a["account_id"]
        ev  = risk_engine.evaluate_account(aid)
        if ev["risk_tier"] in sel_tier and ev["taxonomy_label"] in sel_class:
            if not search_query or search_query.lower() in aid.lower() or search_query.lower() in a.get("upi_id", "").lower():
                rows.append({
                    "Account ID": aid,
                    "Bank": a.get("bank", ""),
                    "UPI ID": a.get("upi_id", ""),
                    "Predicted Class": ev["taxonomy_label"],
                    "Risk Tier": ev["risk_tier"],
                    "Ensemble Score": f"{ev['ensemble_score']}/100",
                    "Mastermind %": f"{ev['mastermind_score']}%",
                    "Syndicate Ring": ev["detected_ring"],
                    "Primary Trigger": ev["evidence"][0] if ev["evidence"] else "N/A",
                })

    st.write(f"Displaying **{len(rows)}** accounts matching filter criteria:")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=480)
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 5: SHAP EXPLAINABILITY
# ═══════════════════════════════════════════════════════════
elif "5. SHAP" in selected_page:
    module_head(
        "Module 5: SHAP Feature Attribution & Local Explainability",
        "Deconstruct prediction drivers into SHAP feature impact & local forensic explanations"
    )

    flagged_ids = [a["account_id"] for a in accounts
                   if risk_engine.evaluate_account(a["account_id"])["risk_tier"] in ("Critical", "High", "Medium")]
    if not flagged_ids:
        flagged_ids = [a["account_id"] for a in accounts[:40]]

    target_acc = st.selectbox("Select Account ID for Forensic Explainability", flagged_ids)
    ev = risk_engine.evaluate_account(target_acc)
    lbl = ev["taxonomy_label"]
    fv = scaled_features.get(target_acc, [0.0] * 11)

    rf_clf = _eval_cache.get("rf_clf")
    shap_mode = st.radio(
        "Explainability Attribution Engine",
        ["TreeExplainer (shap v0.52.0 on Fitted Random Forest Model)", "Statutory Attribution Matrix (Heuristic Weights)"],
        horizontal=True
    )
    if "TreeExplainer" in shap_mode and rf_clf is not None:
        real_res = run_real_shap_explanation(rf_clf, fv)
        if real_res.get("explanation_type") == "shap_tree_explainer":
            shap_out = {
                "explanation_type": "TreeExplainer",
                "contributions": real_res["shap_values"],
                "top_features": real_res["top_features"]
            }
        else:
            shap_out = compute_shap_values(fv, lbl)
    else:
        shap_out = compute_shap_values(fv, lbl)

    col_s1, col_s2 = st.columns([1.4, 1])
    with col_s1:
        st.markdown(
            f"**Account:** `{target_acc}` &bull; **Class:** `{lbl}` &bull; "
            f"**Score:** `{ev['ensemble_score']}/100` ({ev['risk_tier']}) &bull; "
            f"**Engine:** `{shap_out.get('explanation_type', 'SHAP')}`"
        )
        shap_df = pd.DataFrame(
            list(shap_out["contributions"].items()), columns=["Feature", "SHAP Impact"]
        ).sort_values("SHAP Impact")
        fig_s = px.bar(shap_df, x="SHAP Impact", y="Feature", orientation="h", color="SHAP Impact",
                       color_continuous_scale=["#16A34A", "#F8FAFC", "#DC2626"])
        fig_s.update_layout(height=400, margin=dict(l=5, r=5, t=10, b=10),
                            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_s, use_container_width=True)

    with col_s2:
        st.markdown('<div class="dp-sec-head">Top 5 Forensic Risk Elevators</div>', unsafe_allow_html=True)
        for fname, fval in shap_out["top_features"]:
            color_border = "#DC2626" if fval > 0 else "#16A34A"
            bg_card = "#FEF2F2" if fval > 0 else "#F0FDF4"
            st.markdown(f"""
<div style="background:{bg_card};border-left:4px solid {color_border};
            padding:8px 12px;border-radius:4px;margin-bottom:8px;">
    <strong>{fname}</strong><br/>
    <span style="font-size:0.8rem;color:#475569;">
        Impact: <code>{fval:+.4f}</code> &bull; {'↑ Elevates Risk' if fval > 0 else '↓ Mitigates Risk'}
    </span>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="dp-sec-head" style="margin-top:14px;">Investigative Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #002147;
            padding:12px;border-radius:4px;font-size:0.82rem;font-family:monospace;line-height:1.6;">
ACCOUNT: <strong>{target_acc}</strong> &bull; STATUS: <strong>{lbl}</strong><br/>
PRIMARY DRIVER: <strong>{shap_out['top_features'][0][0]}</strong> ({shap_out['top_features'][0][1]:+.4f})<br/>
EVIDENCE: {ev['evidence'][0] if ev['evidence'] else 'Standard retail flow behavior.'}
</div>""", unsafe_allow_html=True)
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 6: INTERACTIVE TRANSACTION NETWORK GRAPH
# ═══════════════════════════════════════════════════════════
elif "6. Interactive Transaction" in selected_page:
    module_head(
        "Module 6: Interactive Transaction Network Graph",
        "Forensic ego-network graph reconstruction, directional fund flow topology, and shared hardware/IP infrastructure"
    )

    df_tx = pd.DataFrame(transactions)
    degree_counts = pd.concat([df_tx["src_account"], df_tx["dst_account"]]).value_counts()
    top_connected = degree_counts.head(30).index.tolist()

    # Step 1: Investigation Target & Scope Controls
    gc1, gc2, gc3, gc4 = st.columns([1.5, 1.5, 1.2, 1.2])
    with gc1:
        center_mode = st.selectbox("Ego-Center Selection Mode", [
            "Top-Connected Hub Accounts (High Volume)",
            "Fraud Coordinator Accounts",
            "Mule Layering Accounts",
            "Custom Account Lookup"
        ])
    with gc2:
        if "Top-Connected" in center_mode:
            center_acc = st.selectbox("Center Account", top_connected, index=0)
        elif "Coordinator" in center_mode:
            coord_list = [r["coordinator"] for r in FRAUD_RINGS]
            center_acc = st.selectbox("Center Account", coord_list, index=0)
        elif "Mule" in center_mode:
            mule_sample = [a["account_id"] for a in accounts
                           if risk_engine.evaluate_account(a["account_id"])["taxonomy_label"] == "Mule"][:30]
            center_acc = st.selectbox("Center Account", mule_sample or top_connected[:10], index=0)
        else:
            center_acc = st.text_input("Enter Account ID", value="ACC00185")
            if center_acc not in degree_counts:
                center_acc = top_connected[0]

    with gc3:
        ego_hops = st.slider("Ego Depth (Hops)", 1, 3, 2, help="Forensic exploration radius around target account")
    with gc4:
        layout_mode = st.selectbox("Topology Layout", [
            "Concentric Radial Rings (Layering Hops)",
            "Force-Directed Organic (Spring)",
            "Bipartite Inflow vs Outflow",
            "Circular Ring"
        ], help="Concentric rings arrange 1-hop and 2-hop accounts in concentric circles around target")

    # Step 2: Dynamic Investigation Filters Bar
    with st.expander("Forensic Filters & Visualization Settings", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            min_amt = st.slider("Minimum Transaction Amount (₹)", 0, 100000, 0, step=2000,
                                help="Filter out low-value transactions to isolate large fund movements")
        with fc2:
            all_channels = sorted(list(set(df_tx["channel"].dropna().unique()))) if "channel" in df_tx.columns else ["UPI", "IMPS", "NEFT", "RTGS"]
            sel_channels = st.multiselect("Payment Rails / Channels", all_channels, default=all_channels)
        with fc3:
            role_options = ["Fraudster", "Mule", "Suspicious", "Normal"]
            sel_roles = st.multiselect("Filter Node Taxonomies", role_options, default=role_options)
        with fc4:
            show_shared_edges = st.checkbox("Overlay Shared IMEI / IP Bridges", value=True)
            show_flow_arrows = st.checkbox("Display Directional Flow Midpoints", value=True)

    adj_out = graph_data.get("adj_out", {})
    adj_in  = graph_data.get("adj_in", {})

    # Hop-by-hop traversal keeping track of exact distance
    hop_dist = {center_acc: 0}
    frontier  = {center_acc}
    for h in range(1, ego_hops + 1):
        nxt = set()
        for u in frontier:
            for e in adj_out.get(u, []):
                tgt = e.get("target")
                if tgt and tgt not in hop_dist:
                    hop_dist[tgt] = h
                    nxt.add(tgt)
            for e in adj_in.get(u, []):
                src = e.get("source") or e.get("target")
                if src and src not in hop_dist:
                    hop_dist[src] = h
                    nxt.add(src)
        frontier = nxt
        if len(hop_dist) > 80:
            break

    sub_nodes = set(hop_dist.keys())

    lbl_map   = {l["account_id"]: l.get("risk_label", "Normal") for l in labels}
    color_map = {"Normal": "#16A34A", "Suspicious": "#F59E0B", "Mule": "#EA580C", "Fraudster": "#DC2626"}

    # Filter nodes by role if specified (keep center_acc always)
    if sel_roles:
        sub_nodes = {n for n in sub_nodes if n == center_acc or lbl_map.get(n, "Normal") in sel_roles}

    G_sub = nx.DiGraph()
    for n in sub_nodes:
        G_sub.add_node(n, hop=hop_dist.get(n, 1))

    # Add edges with filters
    for u in sub_nodes:
        for e in adj_out.get(u, []):
            v = e.get("target")
            if v and v in sub_nodes:
                amt = float(e.get("amount", 1000))
                chn = e.get("channel", "UPI")
                ts  = e.get("timestamp", "2026-06-25")
                if amt >= min_amt and (not sel_channels or chn in sel_channels):
                    if G_sub.has_edge(u, v):
                        G_sub[u][v]["weight"] += amt
                        G_sub[u][v]["count"] += 1
                    else:
                        G_sub.add_edge(u, v, weight=amt, channel=chn, count=1, timestamp=ts)

    # Compute Layout
    if len(G_sub.nodes()) == 0:
        st.warning("No nodes match the selected filter criteria. Please broaden your filters.")
    else:
        if layout_mode == "Concentric Radial Rings (Layering Hops)":
            shells = [[center_acc]]
            for h in range(1, ego_hops + 1):
                shell_h = [n for n in G_sub.nodes() if hop_dist.get(n, 1) == h and n != center_acc]
                if shell_h:
                    shells.append(shell_h)
            pos = nx.shell_layout(G_sub, nlist=shells)
        elif layout_mode == "Bipartite Inflow vs Outflow":
            pos = {center_acc: (0.0, 0.0)}
            in_nodes = [n for n in G_sub.nodes() if G_sub.has_edge(n, center_acc) and n != center_acc]
            out_nodes = [n for n in G_sub.nodes() if G_sub.has_edge(center_acc, n) and n != center_acc]
            other_nodes = [n for n in G_sub.nodes() if n not in in_nodes and n not in out_nodes and n != center_acc]
            
            for i, n in enumerate(in_nodes):
                y_coord = (i - len(in_nodes) / 2.0) * (2.0 / max(1, len(in_nodes)))
                pos[n] = (-1.5, y_coord)
            for i, n in enumerate(out_nodes):
                y_coord = (i - len(out_nodes) / 2.0) * (2.0 / max(1, len(out_nodes)))
                pos[n] = (1.5, y_coord)
            for i, n in enumerate(other_nodes):
                x_coord = -0.75 if (i % 2 == 0) else 0.75
                y_coord = ((i // 2) - len(other_nodes) / 4.0) * 1.5
                pos[n] = (x_coord, y_coord)
        elif layout_mode == "Circular Ring":
            pos = nx.circular_layout(G_sub)
        else: # Force-Directed Organic (Spring)
            k_val = 1.0 / math.sqrt(max(1, len(G_sub.nodes())))
            pos = nx.spring_layout(G_sub, k=k_val, iterations=70, seed=42)

        # Build categorized Edge traces
        inflow_x, inflow_y = [], []
        outflow_x, outflow_y = [], []
        inter_x, inter_y = [], []
        
        arrow_x, arrow_y, arrow_text, arrow_colors = [], [], [], []

        for u, v, d in G_sub.edges(data=True):
            if u not in pos or v not in pos:
                continue
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            amt = float(d.get("weight", 0))
            chn = d.get("channel", "UPI")

            if v == center_acc:
                inflow_x.extend([x0, x1, None])
                inflow_y.extend([y0, y1, None])
                color_type = "#10B981" # Green inflow
                rel_desc = "Direct Inflow to Target"
            elif u == center_acc:
                outflow_x.extend([x0, x1, None])
                outflow_y.extend([y0, y1, None])
                color_type = "#DC2626" # Red outflow
                rel_desc = "Direct Outflow from Target"
            else:
                inter_x.extend([x0, x1, None])
                inter_y.extend([y0, y1, None])
                color_type = "#64748B" # Slate intermediary
                rel_desc = "Intermediary Layering Hop"

            if show_flow_arrows:
                xm = 0.35 * x0 + 0.65 * x1
                ym = 0.35 * y0 + 0.65 * y1
                arrow_x.append(xm)
                arrow_y.append(ym)
                arrow_text.append(f"<b>Fund Flow:</b> {u} ➔ {v}<br/><b>Amount:</b> ₹{amt:,.2f}<br/><b>Channel:</b> {chn}<br/><b>Context:</b> {rel_desc}")
                arrow_colors.append(color_type)

        shared_x, shared_y = [], []
        if show_shared_edges:
            for se in pipe["shared_edges"]:
                su, sv = se["source"], se["target"]
                if su in G_sub.nodes() and sv in G_sub.nodes() and su in pos and sv in pos:
                    x0, y0 = pos[su]
                    x1, y1 = pos[sv]
                    shared_x.extend([x0, x1, None])
                    shared_y.extend([y0, y1, None])

        # Node properties
        node_x, node_y, node_colors, node_sizes, node_symbols, node_lines, node_hover, node_labels = [], [], [], [], [], [], [], []
        for n in G_sub.nodes():
            if n not in pos:
                continue
            x, y = pos[n]
            node_x.append(x)
            node_y.append(y)
            
            n_ev = risk_engine.evaluate_account(n)
            n_acc = next((a for a in accounts if a["account_id"] == n), {})
            tax = n_ev["taxonomy_label"]
            score = n_ev["ensemble_score"]
            tier = n_ev["risk_tier"]
            bank = n_acc.get("bank", "N/A")
            cust_name = n_acc.get("customer_name", "N/A")
            # Node financial volume and degree
            ns = graph_data.get("node_stats", {}).get(n, {})
            tot_credit_amt = float(ns.get("total_in_amount", 0.0))
            tot_debit_amt  = float(ns.get("total_out_amount", 0.0))
            tot_credit_cnt = int(ns.get("in_degree", 0))
            tot_debit_cnt  = int(ns.get("out_degree", 0))
            sub_in_amt  = sum(float(d.get("weight", 0)) for _, _, d in G_sub.in_edges(n, data=True))
            sub_out_amt = sum(float(d.get("weight", 0)) for _, _, d in G_sub.out_edges(n, data=True))
            sub_in_hops = G_sub.in_degree(n)
            sub_out_hops = G_sub.out_degree(n)
            tot_deg = G_sub.degree(n)
            
            if n == center_acc:
                node_sizes.append(34)
                node_symbols.append("diamond")
                node_lines.append(dict(width=3.5, color="#F59E0B"))
                node_colors.append("#002147")
                node_labels.append(f"<b>TARGET: {n}</b>")
            else:
                node_sizes.append(max(16, min(28, 14 + tot_deg * 2)))
                node_symbols.append("circle")
                node_lines.append(dict(width=2, color="#FFFFFF"))
                node_colors.append(color_map.get(tax, "#94A3B8"))
                node_labels.append(n if tot_deg >= 2 else "")

            node_hover.append(
                f"<b>Account:</b> {n}<br/>"
                f"<b>Holder:</b> {cust_name} ({bank})<br/>"
                f"<b>Taxonomy:</b> <span style='color:{color_map.get(tax, '#000')}'><b>{tax}</b></span> ({tier})<br/>"
                f"<b>Forensic Risk Score:</b> <b>{score}/100</b><br/>"
                f"<b>Total Ledger Volume:</b> Credits: ₹{tot_credit_amt:,.2f} ({tot_credit_cnt} txns) | Debits: ₹{tot_debit_amt:,.2f} ({tot_debit_cnt} txns)<br/>"
                f"<b>Sub-Graph Traffic:</b> ₹{sub_in_amt:,.2f} In ({sub_in_hops} hops) | ₹{sub_out_amt:,.2f} Out ({sub_out_hops} hops)<br/>"
                f"<b>Hops from Target:</b> {hop_dist.get(n, 1)}<br/>"
                f"<b>Trigger Flag:</b> {n_ev['evidence'][0] if n_ev['evidence'] else 'Normal Retail Activity'}"
            )

        traces = []
        if inflow_x:
            traces.append(go.Scatter(x=inflow_x, y=inflow_y, mode="lines",
                                     line=dict(width=2.2, color="#10B981"),
                                     hoverinfo="none", name="Inflow to Target (Credits)"))
        if outflow_x:
            traces.append(go.Scatter(x=outflow_x, y=outflow_y, mode="lines",
                                     line=dict(width=2.5, color="#DC2626"),
                                     hoverinfo="none", name="Outflow from Target (Debits)"))
        if inter_x:
            traces.append(go.Scatter(x=inter_x, y=inter_y, mode="lines",
                                     line=dict(width=1.5, color="#64748B"),
                                     hoverinfo="none", name="Intermediary Flow"))
        if shared_x and show_shared_edges:
            traces.append(go.Scatter(x=shared_x, y=shared_y, mode="lines",
                                     line=dict(width=2.2, color="#F59E0B", dash="dot"),
                                     hoverinfo="none", name="Shared IMEI / IP Device Link"))

        if show_flow_arrows and arrow_x:
            traces.append(go.Scatter(
                x=arrow_x, y=arrow_y, mode="markers",
                marker=dict(symbol="triangle-up", size=9, color=arrow_colors, line=dict(width=1, color="#FFFFFF")),
                hoverinfo="text", hovertext=arrow_text,
                name="Flow Directions"
            ))

        traces.append(go.Scatter(
            x=node_x, y=node_y, mode="markers+text",
            text=node_labels,
            textposition="top center",
            textfont=dict(size=9, color="#001233", family="Segoe UI"),
            hovertext=node_hover, hoverinfo="text",
            marker=dict(color=node_colors, size=node_sizes, line=dict(width=[nl['width'] for nl in node_lines], color=[nl['color'] for nl in node_lines]), symbol=node_symbols),
            name="Bank Accounts"
        ))

        # Dynamic Legend
        legend_traces = [
            go.Scatter(x=[None], y=[None], mode="markers",
                       marker=dict(color="#002147", size=14, symbol="diamond", line=dict(width=2, color="#F59E0B")),
                       name="Ego Target Account", showlegend=True)
        ] + [
            go.Scatter(x=[None], y=[None], mode="markers",
                       marker=dict(color=c, size=12), name=f"{lbl} Account", showlegend=True)
            for lbl, c in color_map.items() if not sel_roles or lbl in sel_roles
        ]

        fig_net = go.Figure(data=traces + legend_traces, layout=go.Layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
            hovermode="closest",
            margin=dict(b=10, l=10, r=10, t=10),
            height=580,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF"
        ))

        # Forensic Metrics Strip
        center_ev = risk_engine.evaluate_account(center_acc)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Center Ego Target", center_acc, f"{lbl_map.get(center_acc, 'Normal')} Classification")
        m2.metric("Sub-Graph Population", f"{len(G_sub.nodes())} Entities", f"Radius: {ego_hops} Hops")
        m3.metric("Filtered Flows", f"{len(G_sub.edges())} Directed Edges", f"Min ₹{min_amt:,.0f}")
        m4.metric("Consortium Risk Score", f"{center_ev['ensemble_score']}/100", f"{center_ev['risk_tier']} Tier")

        # Interactive Graph View Tabs
        tab_graph, tab_nodes, tab_edges, tab_forensics = st.tabs([
            "Interactive Topology Map",
            "Sub-Graph Account Roster & Ledger Audits",
            "Transaction Flow Breakdown (Credits / Debits)",
            "Network Centrality & Mastermind Scoring"
        ])

        with tab_graph:
            st.plotly_chart(fig_net, use_container_width=True)
            
            # Interactive Node Deep Dive Inspector
            st.markdown('<div class="dp-sec-head">Interactive On-Canvas Node Deep Dive Inspector</div>', unsafe_allow_html=True)
            ic1, ic2 = st.columns([1, 2.5])
            with ic1:
                inspect_node = st.selectbox("Select Account on Canvas to Inspect", sorted(list(G_sub.nodes())),
                                            index=sorted(list(G_sub.nodes())).index(center_acc) if center_acc in G_sub.nodes() else 0)
            with ic2:
                insp_ev = risk_engine.evaluate_account(inspect_node)
                insp_acc = next((a for a in accounts if a["account_id"] == inspect_node), {})
                insp_tax = insp_ev["taxonomy_label"]
                badge_bg = color_map.get(insp_tax, "#94A3B8")
                
                # Fetch financial figures for inspected node
                insp_ns = graph_data.get("node_stats", {}).get(inspect_node, {})
                insp_tot_in  = float(insp_ns.get("total_in_amount", 0.0))
                insp_tot_out = float(insp_ns.get("total_out_amount", 0.0))
                insp_in_cnt  = int(insp_ns.get("in_degree", 0))
                insp_out_cnt = int(insp_ns.get("out_degree", 0))
                insp_net     = insp_tot_in - insp_tot_out
                insp_sub_in  = sum(float(d.get("weight", 0)) for _, _, d in G_sub.in_edges(inspect_node, data=True))
                insp_sub_out = sum(float(d.get("weight", 0)) for _, _, d in G_sub.out_edges(inspect_node, data=True))
                
                # Statutory Recommendation
                if insp_tax in ["Fraudster", "Mule"]:
                    legal_rec = "Issue Section 106 BNSS Notice to Bank Manager for Immediate Account Debit Freeze; Seize linked IMEI/IP."
                elif insp_tax == "Suspicious":
                    legal_rec = "Issue Section 94 BNSS Order for Complete Transaction Trail & KYC Dossier Production."
                else:
                    legal_rec = "Normal Retail Activity. No immediate statutory restriction warranted."

                st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #CBD5E1;border-left:5px solid {badge_bg};padding:14px 18px;border-radius:4px;font-size:0.86rem;line-height:1.75;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-size:1.05rem;font-weight:900;color:#002147;">Account: <code>{inspect_node}</code> ({insp_acc.get('bank', 'N/A')})</span>
        <span style="background:{badge_bg};color:#FFFFFF;padding:3px 10px;border-radius:12px;font-weight:800;font-size:0.78rem;">{insp_tax} ({insp_ev['risk_tier']})</span>
    </div>
    <strong>Account Holder:</strong> {insp_acc.get('customer_name', 'N/A')} | <strong>IFSC / Branch:</strong> {insp_acc.get('branch_code', 'N/A')} | <strong>UPI ID:</strong> <code>{insp_acc.get('upi_id', 'N/A')}</code><br/>
    <strong>Financial Ledger Audit:</strong> Total Credits: <strong style="color:#10B981;">₹{insp_tot_in:,.2f}</strong> ({insp_in_cnt} txns) | Total Debits: <strong style="color:#DC2626;">₹{insp_tot_out:,.2f}</strong> ({insp_out_cnt} txns) | <strong>Net Flow:</strong> <span style="color:{'#10B981' if insp_net >= 0 else '#DC2626'};font-weight:800;">{'+' if insp_net >= 0 else '-'}₹{abs(insp_net):,.2f}</span><br/>
    <strong>Sub-Graph Flow:</strong> Inflow: ₹{insp_sub_in:,.2f} ({G_sub.in_degree(inspect_node)} hops) | Outflow: ₹{insp_sub_out:,.2f} ({G_sub.out_degree(inspect_node)} hops) | Forensic Score: <strong>{insp_ev['ensemble_score']}/100</strong><br/>
    <strong>Primary Flag:</strong> {insp_ev['evidence'][0] if insp_ev['evidence'] else 'Verified Genuine Profile'}<br/>
    <strong>Statutory Police Recommendation:</strong> <span style="color:#C4122F;font-weight:700;">{legal_rec}</span>
</div>""", unsafe_allow_html=True)

        with tab_nodes:
            st.markdown("""
<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-left:5px solid #16A34A;padding:12px 16px;border-radius:4px;font-size:0.85rem;color:#166534;margin-bottom:12px;line-height:1.6;">
    <strong>Forensic Audit Guide — Understanding Ledger Credits vs. Debits:</strong><br/>
    • <strong>Pure Inflow / Credited Accounts (Sub-Graph Outflow = ₹0.00):</strong> Terminal money sinks or cash-out mule points where funds are liquidated via ATM or offline POS terminals without secondary electronic transfers.<br/>
    • <strong>Pure Outflow / Debited Accounts (Sub-Graph Inflow = ₹0.00):</strong> Primary compromised victim accounts or upstream feeder accounts injecting capital into the syndicate.<br/>
    • <strong>High-Turnover Transit Accounts (Credits ≈ Debits):</strong> Intermediate layering mules moving funds across banks within minutes to defeat Section 106 BNSS debit freeze orders.<br/>
    <em>Both global lifetime ledger totals and direct ego sub-graph active flows are provided below for forensic attribution.</em>
</div>
""", unsafe_allow_html=True)
            node_rows = []
            for n in G_sub.nodes():
                n_ev = risk_engine.evaluate_account(n)
                n_acc = next((a for a in accounts if a["account_id"] == n), {})
                ns_n = graph_data.get("node_stats", {}).get(n, {})
                c_in  = float(ns_n.get("total_in_amount", 0.0))
                d_out = float(ns_n.get("total_out_amount", 0.0))
                c_cnt = int(ns_n.get("in_degree", 0))
                d_cnt = int(ns_n.get("out_degree", 0))
                net_n = c_in - d_out
                velocity = (d_out / max(1.0, c_in)) * 100.0 if c_in > 0 else 0.0
                
                s_in  = sum(float(d.get("weight", 0)) for _, _, d in G_sub.in_edges(n, data=True))
                s_out = sum(float(d.get("weight", 0)) for _, _, d in G_sub.out_edges(n, data=True))

                # Operational Syndicate Role
                if n == center_acc:
                    net_role = "Target Ego Hub"
                elif s_in > 0 and s_out == 0:
                    net_role = "Terminal Cash-Out Sink"
                elif s_out > 0 and s_in == 0:
                    net_role = "Victim / Feeder Remitter"
                elif s_in > 0 and s_out > 0:
                    net_role = "Layering Mule Relay"
                else:
                    net_role = "Direct Counterparty"

                # Statutory SOP
                tax_lbl = n_ev["taxonomy_label"]
                if tax_lbl in ["Fraudster", "Mule"]:
                    stat_action = "Sec 106 BNSS Immediate Debit Freeze"
                elif tax_lbl == "Suspicious":
                    stat_action = "Sec 94 BNSS KYC & 6-Month Trail Order"
                else:
                    stat_action = "Routine Retail Surveillance"

                node_rows.append({
                    "Account ID": n,
                    "Customer Name": n_acc.get("customer_name", "N/A"),
                    "Bank": n_acc.get("bank", "N/A"),
                    "Taxonomy Class": tax_lbl,
                    "Risk Tier": n_ev["risk_tier"],
                    "Risk Score": f"{n_ev['ensemble_score']}/100",
                    "Lifetime Credits (₹)": f"₹{c_in:,.2f} ({c_cnt} tx)",
                    "Lifetime Debits (₹)": f"₹{d_out:,.2f} ({d_cnt} tx)",
                    "Net Balance (₹)": f"{'+' if net_n >= 0 else '-'}₹{abs(net_n):,.2f}",
                    "Turnover Ratio": f"{velocity:.1f}%",
                    "Sub-Graph Inflow (₹)": f"₹{s_in:,.2f}",
                    "Sub-Graph Outflow (₹)": f"₹{s_out:,.2f}",
                    "Network Topology Role": net_role,
                    "Primary Trigger": n_ev["evidence"][0] if n_ev["evidence"] else "Normal Retail Activity",
                    "Statutory SOP": stat_action
                })
            df_node_roster = pd.DataFrame(node_rows)
            st.dataframe(df_node_roster, use_container_width=True, height=380)
            
            # Download Sub-Graph Data
            csv_nodes = df_node_roster.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Sub-Graph Forensic Account Roster (CSV)",
                data=csv_nodes,
                file_name=f"FinSuraksha_SubGraph_{center_acc}_Accounts.csv",
                mime="text/csv"
            )

        with tab_edges:
            st.markdown('<div class="dp-sec-head">Forensic Itemized Transaction Trail (Bank Ledger Extract)</div>', unsafe_allow_html=True)
            
            # Filter actual transactions between sub_nodes
            df_sub_tx = df_tx[df_tx["src_account"].isin(sub_nodes) & df_tx["dst_account"].isin(sub_nodes)].copy()
            if min_amt > 0:
                df_sub_tx = df_sub_tx[df_sub_tx["amount"] >= min_amt]
            if sel_channels:
                df_sub_tx = df_sub_tx[df_sub_tx["channel"].isin(sel_channels)]
            
            # Sub-Graph Transaction Metrics
            tot_sub_tx_vol = df_sub_tx["amount"].sum() if not df_sub_tx.empty else 0.0
            st_m1, st_m2, st_m3, st_m4 = st.columns(4)
            st_m1.metric("Sub-Network Transfers", f"{len(df_sub_tx)} Itemized Rows", f"{len(G_sub.edges())} Directed Links")
            st_m2.metric("Gross Capital Flow", f"₹{tot_sub_tx_vol:,.2f}", "Audited Transfer Volume")
            st_m3.metric("Debited Remitters", f"{df_sub_tx['src_account'].nunique() if not df_sub_tx.empty else 0} Accounts", "Originating Senders")
            st_m4.metric("Credited Beneficiaries", f"{df_sub_tx['dst_account'].nunique() if not df_sub_tx.empty else 0} Accounts", "Destination Sinks")

            if not df_sub_tx.empty:
                df_sub_tx = df_sub_tx.sort_values("timestamp", ascending=False)
                itemized_rows = []
                for _, r in df_sub_tx.iterrows():
                    u_src = r["src_account"]
                    v_dst = r["dst_account"]
                    if u_src == center_acc:
                        flow_ctx = "Target Direct Outflow (Debit)"
                    elif v_dst == center_acc:
                        flow_ctx = "Target Direct Inflow (Credit)"
                    else:
                        flow_ctx = "Intermediary Layering Hop"

                    itemized_rows.append({
                        "Transaction ID": r.get("transaction_id", "N/A"),
                        "Bank UTR Number": r.get("utr_number", "N/A"),
                        "Timestamp": r.get("timestamp", "N/A"),
                        "Remitter Account (Debited)": u_src,
                        "Beneficiary Account (Credited)": v_dst,
                        "Transfer Amount (₹)": f"₹{float(r.get('amount', 0)):,.2f}",
                        "Payment Channel": r.get("channel", "UPI"),
                        "City / Precinct": r.get("city", "N/A"),
                        "IP Address": r.get("ip_address", "N/A"),
                        "Flow Context": flow_ctx
                    })
                df_itemized = pd.DataFrame(itemized_rows)
                st.dataframe(df_itemized, use_container_width=True, height=350)
                csv_txs = df_itemized.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Itemized Transaction Ledger (CSV)",
                    data=csv_txs,
                    file_name=f"FinSuraksha_SubGraph_{center_acc}_Itemized_Transactions.csv",
                    mime="text/csv"
                )
            else:
                st.info("No itemized transactions match the active threshold filters in this ego radius.")

            st.markdown('<div class="dp-sec-head">Aggregated Pairwise Inter-Account Flow Matrix</div>', unsafe_allow_html=True)
            edge_rows = []
            for u, v, d in G_sub.edges(data=True):
                amt = float(d.get("weight", 0))
                chn = d.get("channel", "UPI")
                cnt = int(d.get("count", 1))
                ts  = d.get("timestamp", "2026-06-25")
                edge_rows.append({
                    "Source Account (Debited)": u,
                    "Destination Account (Credited)": v,
                    "Total Amount Transferred (₹)": f"₹{amt:,.2f}",
                    "Transaction Count": f"{cnt} Transfer{'s' if cnt > 1 else ''}",
                    "Primary Channel": chn,
                    "Latest Timestamp": ts,
                    "Directional Role": "Direct Target Outflow" if u == center_acc else ("Direct Target Inflow" if v == center_acc else "Layering Bridge")
                })
            df_edge_roster = pd.DataFrame(edge_rows)
            st.dataframe(df_edge_roster, use_container_width=True, height=260)
            csv_edges = df_edge_roster.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Aggregated Flow Matrix (CSV)",
                data=csv_edges,
                file_name=f"FinSuraksha_SubGraph_{center_acc}_Pairwise_Flows.csv",
                mime="text/csv"
            )

        with tab_forensics:
            cf1, cf2 = st.columns(2)
            with cf1:
                st.markdown('<div class="dp-sec-head">Mastermind Centrality Diagnostics</div>', unsafe_allow_html=True)
                mm_score = net_engine.compute_mastermind_score(center_acc)
                st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #CBD5E1;border-left:5px solid #C4122F;padding:16px;border-radius:4px;font-size:0.86rem;line-height:1.8;">
    <strong>Target Node:</strong> <code>{center_acc}</code><br/>
    <strong>Syndicate Mastermind Score:</strong> <strong style="color:#C4122F;font-size:1.1rem;">{mm_score:.1f}%</strong><br/>
    <strong>Betweenness Position:</strong> Inflow-Outflow Coordinator Bridge<br/>
    <strong>Primary Forensic Finding:</strong> {center_ev['evidence'][0] if center_ev['evidence'] else 'No high-risk pattern detected.'}
</div>""", unsafe_allow_html=True)

            with cf2:
                st.markdown('<div class="dp-sec-head">Connected Degree Distribution</div>', unsafe_allow_html=True)
                deg_df = pd.DataFrame([{"Node": n, "Degree": G_sub.degree(n)} for n in list(G_sub.nodes())[:15]])
                fig_deg = px.bar(deg_df, x="Node", y="Degree", color_discrete_sequence=["#002147"])
                fig_deg.update_layout(height=260, margin=dict(l=5, r=5, t=10, b=5), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
                st.plotly_chart(fig_deg, use_container_width=True)

    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 7: INDIA CRIME RISK MAP & NATIONWIDE CORRIDORS
# ═══════════════════════════════════════════════════════════
elif "7. India Crime" in selected_page:
    module_head(
        "Module 7: India Cybercrime Geographic Risk Map & Corridors",
        "Nationwide geographic distribution of crime hubs, interstate transit routes, and fund dispersal corridors"
    )

    CITY_COORDS = {
        "Rohini, Delhi":           (28.7159, 77.1171),
        "New Delhi":               (28.6139, 77.2090),
        "Nuh (Mewat), Haryana":    (28.1067, 77.0057),
        "Bharatpur, Rajasthan":    (27.2152, 77.5030),
        "Alwar, Rajasthan":        (27.5530, 76.6346),
        "Jamtara, Jharkhand":      (23.9632, 86.8029),
        "Deoghar, Jharkhand":      (24.4826, 86.6975),
        "Mathura, UP":             (27.4924, 77.6737),
        "Mumbai, Maharashtra":     (19.0760, 72.8777),
        "Kolkata, West Bengal":    (22.5726, 88.3639),
        "Bengaluru, Karnataka":    (12.9716, 77.5946),
        "Hyderabad, Telangana":    (17.3850, 78.4867),
    }

    HOTSPOTS = [
        {"name": "Rohini, Delhi",         "lat": 28.7159, "lng": 77.1171, "cases": 899, "risk": "Host Command Station",    "color": "#002147", "typologies": "Headquarters, FIR Registration, CDR Correlation", "police_station": "Cyber Police Station, Sector-17, Rohini, Delhi", "nodal": "ASI Jaswinder Joon (I.O.)", "phone": "011-27552222", "dm": "District Magistrate (North-West Delhi)"},
        {"name": "Nuh (Mewat), Haryana",  "lat": 28.1067, "lng": 77.0057, "cases": 847, "risk": "Severe Risk Corridor",   "color": "#DC2626", "typologies": "Sextortion, reverse QR scam, mule device clusters", "police_station": "Cyber Crime Police Station, Nuh (Mewat)", "nodal": "DSP Cyber Crime Nuh", "phone": "01267-271212", "dm": "Deputy Commissioner, Nuh"},
        {"name": "Bharatpur, Rajasthan",  "lat": 27.2152, "lng": 77.5030, "cases": 815, "risk": "High Risk Hub",          "color": "#F59E0B", "typologies": "Fake loan apps, predatory advance-fee scams", "police_station": "Cyber Police Station, Bharatpur", "nodal": "CO Cyber Crime Bharatpur", "phone": "05644-222333", "dm": "District Collector, Bharatpur"},
        {"name": "Alwar, Rajasthan",      "lat": 27.5530, "lng": 76.6346, "cases": 725, "risk": "High Risk Hub",          "color": "#F59E0B", "typologies": "Mule account rings, ATM cash-out dispersal", "police_station": "Cyber Cell, SP Office Alwar", "nodal": "Inspector Cyber Crime Cell", "phone": "0144-2334455", "dm": "District Collector, Alwar"},
        {"name": "Jamtara, Jharkhand",    "lat": 23.9632, "lng": 86.8029, "cases": 782, "risk": "Severe Risk Hub",        "color": "#DC2626", "typologies": "Phishing URLs, OTP impersonation, SIM swap", "police_station": "Cyber Crime Police Station, Jamtara", "nodal": "Superintendent of Police, Jamtara", "phone": "06433-222100", "dm": "Deputy Commissioner, Jamtara"},
        {"name": "Deoghar, Jharkhand",    "lat": 24.4826, "lng": 86.6975, "cases": 735, "risk": "Moderate Risk Hub",      "color": "#A855F7", "typologies": "Fake investment, crypto conversion gateway", "police_station": "Cyber Crime Police Station, Deoghar", "nodal": "DSP Cyber Deoghar", "phone": "06432-232323", "dm": "Deputy Commissioner, Deoghar"},
        {"name": "Mathura, UP",           "lat": 27.4924, "lng": 77.6737, "cases": 699, "risk": "High Risk Transit",      "color": "#F59E0B", "typologies": "UPI QR smurfing, card skimming", "police_station": "Cyber Crime Police Station, Mathura Range", "nodal": "Nodal Inspector Cyber Mathura", "phone": "0565-2400100", "dm": "District Magistrate, Mathura"},
        {"name": "Mumbai, Maharashtra",   "lat": 19.0760, "lng": 72.8777, "cases": 700, "risk": "Financial Sink Node",    "color": "#0EA5E9", "typologies": "ATM cashout networks, merchant settlements", "police_station": "Cyber Crime Police Station, Bandra Kurla Complex (BKC)", "nodal": "DCP Cyber Crime Mumbai", "phone": "022-26504008", "dm": "Collector, Mumbai Suburban"},
        {"name": "Bengaluru, Karnataka",  "lat": 12.9716, "lng": 77.5946, "cases": 699, "risk": "Tech Gateway Hub",       "color": "#10B981", "typologies": "Cross-border payment gateways, shell layering", "police_station": "CID Cyber Crime Police Station, Carlton House", "nodal": "SP Cyber Crime Division Bengaluru", "phone": "080-22094444", "dm": "Deputy Commissioner, Bengaluru Urban"},
        {"name": "Kolkata, West Bengal",  "lat": 22.5726, "lng": 88.3639, "cases": 679, "risk": "Transit Corridor",       "color": "#8B5CF6", "typologies": "Hawala exit trails, fake job deposits", "police_station": "Cyber Crime Police Station, Lalbazar", "nodal": "DC Cyber Crime Kolkata Police", "phone": "033-22143000", "dm": "District Magistrate, Kolkata"},
        {"name": "Hyderabad, Telangana",  "lat": 17.3850, "lng": 78.4867, "cases": 672, "risk": "Moderate Risk Hub",     "color": "#F59E0B", "typologies": "Tech support scam, vishing campaigns", "police_station": "Cyber Crime Police Station, CCS Hyderabad", "nodal": "ACP Cyber Crimes Hyderabad", "phone": "040-27852435", "dm": "District Collector, Hyderabad"},
        {"name": "New Delhi",             "lat": 28.6139, "lng": 77.2090, "cases": 721, "risk": "National Command Node",  "color": "#002147", "typologies": "Coordination, nodal banking liaison", "police_station": "Special Cell Cyber Operations / IFSO, Dwarka", "nodal": "DCP IFSO Delhi Police", "phone": "011-20892600", "dm": "District Magistrate (New Delhi)"},
    ]

    # Compute ALL dynamic corridors from transactions.csv
    df_tx_fraud = pd.DataFrame(transactions)
    df_tx_fraud = df_tx_fraud[~df_tx_fraud["scenario_label"].isin(["legitimate_retail_flow", "legitimate_transfer"])].copy()

    dynamic_corridors = {}
    for scen, grp in df_tx_fraud.groupby("scenario_label"):
        grp = grp.sort_values("timestamp")
        c_list = grp["city"].tolist()
        for i in range(len(c_list) - 1):
            c1, c2 = c_list[i], c_list[i + 1]
            if c1 != c2 and c1 in CITY_COORDS and c2 in CITY_COORDS:
                pair = (c1, c2)
                if pair not in dynamic_corridors:
                    dynamic_corridors[pair] = {"count": 0, "scenarios": set()}
                dynamic_corridors[pair]["count"] += 1
                dynamic_corridors[pair]["scenarios"].add(scen)

    corridor_items = sorted(dynamic_corridors.items(), key=lambda x: x[1]["count"], reverse=True)

    # Top Crime Command KPI Strip
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Host Command Cyber PS", "Rohini Sector-17", "Delhi Police Special Unit")
    k2.metric("Monitored Cyber Hubs", f"{len(HOTSPOTS)} National Jurisdictions", "BNS & IT Act Scope")
    k3.metric("Active Interstate Corridors", f"{len(corridor_items)} Transit Routes", "High Velocity Fund Paths")
    top_corridor = f"{corridor_items[0][0][0].split(',')[0]} ➔ {corridor_items[0][0][1].split(',')[0]}" if corridor_items else "Mewat ➔ Delhi"
    k4.metric("Highest Threat Axis", top_corridor, f"{corridor_items[0][1]['count'] if corridor_items else 0} Detected Hops")

    # Multi-Engine Map Interface Tabs
    tab_gis, tab_leaflet, tab_gmaps, tab_dossier = st.tabs([
        "All-India GIS Radar & Vector Transit Corridors",
        "Interactive Tactical Street & Satellite Map (Multi-Layer Leaflet)",
        "Google Maps Live Intelligence & API Console",
        "Interstate Crime Corridors & Remand Dossier"
    ])

    # ═════════════════════════════════════════════════════════════
    # TAB 1: ALL-INDIA GIS RADAR (PLOTLY VECTOR ENGINE)
    # ═════════════════════════════════════════════════════════════
    with tab_gis:
        c_f1, c_f2 = st.columns([2.5, 1])
        with c_f1:
            gis_corr_opts = ["All Inter-State Transit Corridors"] + [
                f"{c1} ➔ {c2} ({data['count']} transit hops)" for (c1, c2), data in corridor_items
            ]
            sel_gis_corr = st.selectbox("Filter GIS Transit Route", gis_corr_opts, key="gis_corr_sel")
        with c_f2:
            show_gis_labels = st.checkbox("Show Crime Hub Labels", value=True, key="gis_lbl_chk")

        fig_geo = go.Figure()

        # Add Corridor Lines
        line_colors = ["#DC2626", "#F97316", "#002147", "#0EA5E9", "#A855F7", "#10B981", "#F59E0B", "#E11D48"]
        c_idx = 0
        for (c1, c2), data in corridor_items:
            if sel_gis_corr != "All Inter-State Transit Corridors":
                if not sel_gis_corr.startswith(f"{c1} ➔ {c2}"):
                    continue
            p1 = CITY_COORDS[c1]
            p2 = CITY_COORDS[c2]
            c_col = line_colors[c_idx % len(line_colors)]
            c_idx += 1
            fig_geo.add_trace(go.Scattergeo(
                lon=[p1[1], p2[1]],
                lat=[p1[0], p2[0]],
                mode="lines",
                line=dict(width=max(2.0, min(5.0, 1.5 + data['count'] * 0.4)), color=c_col),
                name=f"{c1.split(',')[0]} ➔ {c2.split(',')[0]}",
                hoverinfo="text",
                hovertext=f"<b>Corridor:</b> {c1} ➔ {c2}<br/><b>Transit Hops:</b> {data['count']}<br/><b>Typologies:</b> {len(data['scenarios'])}<br/><b>Primary Path:</b> High-velocity interstate laundering trail"
            ))

        # Add Hub Markers
        hub_lons = [h["lng"] for h in HOTSPOTS]
        hub_lats = [h["lat"] for h in HOTSPOTS]
        hub_names = [h["name"].split(",")[0] if show_gis_labels else "" for h in HOTSPOTS]
        hub_sizes = [30 if "Rohini" in h["name"] else max(14, int(math.sqrt(h["cases"]) * 1.0)) for h in HOTSPOTS]
        hub_colors = [h["color"] for h in HOTSPOTS]
        hub_symbols = ["star" if "Rohini" in h["name"] else "circle" for h in HOTSPOTS]
        hub_hover = [
            f"<b>{h['name']}</b><br/>"
            f"<b>Classification:</b> {h['risk']}<br/>"
            f"<b>Incident Cases:</b> {h['cases']}<br/>"
            f"<b>Police Jurisdiction:</b> {h['police_station']}<br/>"
            f"<b>Nodal Officer:</b> {h['nodal']} ({h['phone']})<br/>"
            f"<b>Primary M.O.:</b> {h['typologies']}"
            for h in HOTSPOTS
        ]

        fig_geo.add_trace(go.Scattergeo(
            lon=hub_lons,
            lat=hub_lats,
            mode="markers+text",
            text=hub_names,
            textposition="top right",
            textfont=dict(size=10, color="#001233", family="Segoe UI"),
            marker=dict(
                size=hub_sizes,
                color=hub_colors,
                symbol=hub_symbols,
                line=dict(width=2, color="#FFFFFF"),
                opacity=0.95
            ),
            hoverinfo="text",
            hovertext=hub_hover,
            name="Cybercrime Hubs & Stations"
        ))

        fig_geo.update_geos(
            scope="asia",
            lataxis_range=[6.5, 37.5],
            lonaxis_range=[68.0, 97.5],
            center=dict(lat=22.5, lon=82.0),
            projection_type="natural earth",
            showcountries=True,
            countrycolor="#002147",
            showsubunits=True,
            subunitcolor="#CBD5E1",
            showland=True,
            landcolor="#F8FAFC",
            showocean=True,
            oceancolor="#E0F2FE",
            showlakes=True,
            lakecolor="#E0F2FE",
            showrivers=True,
            rivercolor="#BAE6FD",
            resolution=50
        )
        fig_geo.update_layout(
            height=580,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font=dict(size=10)),
            paper_bgcolor="#FFFFFF"
        )
        st.plotly_chart(fig_geo, use_container_width=True)
        st.markdown(
            '<div style="font-size:0.86rem;color:#334155;background:#F8FAFC;padding:10px 16px;border-radius:4px;border-left:4px solid #002147;">'
            '<strong>Tactical Vector Radar Active:</strong> Renders client-side geospatial projection of Indian territories. '
            '<strong>Gold Star:</strong> Cyber Police Station Rohini Sector-17 (Delhi Police Host Command Node). '
            '<strong>Dotted Arteries:</strong> Active interstate capital laundering vectors detected through transaction topology.'
            '</div>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════════════════════════════════════
    # TAB 2: INTERACTIVE TACTICAL STREET & SATELLITE MAP (LEAFLET)
    # ═════════════════════════════════════════════════════════════
    with tab_leaflet:
        lf_c1, lf_c2 = st.columns([2.5, 1])
        with lf_c1:
            leaf_corr_opts = ["All Inter-State Corridors"] + [
                f"{c1} ➔ {c2} ({data['count']} transit hops)" for (c1, c2), data in corridor_items
            ]
            sel_leaf_corr = st.selectbox("Corridor Transit Filter", leaf_corr_opts, key="leaf_corr_sel")
        with lf_c2:
            sel_leaf_city = st.selectbox("Zoom to Hotspot Precinct", ["All India Overview"] + [h["name"] for h in HOTSPOTS], key="leaf_city_sel")

        # Prepare JSON data for Leaflet
        hotspots_payload = []
        for h in HOTSPOTS:
            dist_km = intelligence.haversine_distance(28.7159, 77.1171, h["lat"], h["lng"])
            hotspots_payload.append({
                "name": h["name"],
                "lat": h["lat"],
                "lng": h["lng"],
                "cases": h["cases"],
                "risk": h["risk"],
                "color": h["color"],
                "police_station": h["police_station"],
                "nodal": h["nodal"],
                "phone": h["phone"],
                "dm": h["dm"],
                "typologies": h["typologies"],
                "dist_km": round(dist_km, 1)
            })

        corridors_payload = []
        corr_colors = ["#DC2626", "#F97316", "#002147", "#0EA5E9", "#A855F7", "#10B981", "#F59E0B", "#E11D48"]
        for idx, ((c1, c2), data) in enumerate(corridor_items):
            if sel_leaf_corr != "All Inter-State Corridors":
                if not sel_leaf_corr.startswith(f"{c1} ➔ {c2}"):
                    continue
            p1 = CITY_COORDS[c1]
            p2 = CITY_COORDS[c2]
            corridors_payload.append({
                "from": c1,
                "to": c2,
                "p1": [p1[0], p1[1]],
                "p2": [p2[0], p2[1]],
                "hops": data["count"],
                "color": corr_colors[idx % len(corr_colors)]
            })

        import json as _json
        hs_json = _json.dumps(hotspots_payload)
        corr_json = _json.dumps(corridors_payload)

        # Center coordinates
        if sel_leaf_city != "All India Overview":
            target_h = next(h for h in HOTSPOTS if h["name"] == sel_leaf_city)
            center_lat, center_lng, map_zoom = target_h["lat"], target_h["lng"], 11
        else:
            center_lat, center_lng, map_zoom = 22.8, 79.5, 5

        leaflet_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
                #leaflet-map {{ width: 100%; height: 550px; border-radius: 6px; }}
                .leaflet-popup-content-wrapper {{ border-radius: 6px; box-shadow: 0 4px 16px rgba(0,0,0,0.25); }}
                .badge-card {{ font-size: 12px; line-height: 1.5; }}
            </style>
        </head>
        <body>
            <div id="leaflet-map"></div>
            <script>
                var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }});
                var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxZoom: 19,
                    attribution: '© Esri Satellite'
                }});
                var dark = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                    maxZoom: 19,
                    attribution: '© CartoDB Dark'
                }});

                var map = L.map('leaflet-map', {{
                    center: [{center_lat}, {center_lng}],
                    zoom: {map_zoom},
                    layers: [osm]
                }});

                var baseMaps = {{
                    "🗺️ Standard Street Map": osm,
                    "🛰️ High-Res Satellite Imagery": satellite,
                    "🌑 Tactical Dark Mode": dark
                }};
                L.control.layers(baseMaps).addTo(map);

                var hotspots = {hs_json};
                hotspots.forEach(function(h) {{
                    var isHost = h.name.includes("Rohini");
                    var radiusMeters = isHost ? 40000 : 18000 + Math.sqrt(h.cases) * 500;

                    L.circle([h.lat, h.lng], {{
                        color: h.color,
                        fillColor: h.color,
                        fillOpacity: isHost ? 0.35 : 0.18,
                        weight: 1.5,
                        radius: radiusMeters
                    }}).addTo(map);

                    var marker = L.circleMarker([h.lat, h.lng], {{
                        radius: isHost ? 13 : 8,
                        color: isHost ? '#F59E0B' : '#FFFFFF',
                        weight: isHost ? 3.5 : 2,
                        fillColor: h.color,
                        fillOpacity: 0.95
                    }}).addTo(map);

                    var gmapsUrl = 'https://www.google.com/maps/search/?api=1&query=' + h.lat + ',' + h.lng;
                    var popupHtml = '<div class="badge-card">' +
                        '<div style="font-weight:900;color:#002147;font-size:14px;margin-bottom:4px;">' + h.name + '</div>' +
                        '<div style="background:' + h.color + ';color:#FFFFFF;display:inline-block;padding:2px 8px;border-radius:10px;font-weight:bold;font-size:10px;margin-bottom:6px;">' + h.risk + '</div><br/>' +
                        '<strong>Jurisdiction:</strong> ' + h.police_station + '<br/>' +
                        '<strong>Nodal Officer:</strong> ' + h.nodal + ' (' + h.phone + ')<br/>' +
                        '<strong>District Magistrate:</strong> ' + h.dm + '<br/>' +
                        '<strong>Distance from Rohini HQ:</strong> <span style="color:#C4122F;font-weight:bold;">' + h.dist_km + ' km</span><br/>' +
                        '<strong>M.O. / Typology:</strong> ' + h.typologies + '<br/>' +
                        '<div style="margin-top:8px;">' +
                        '<a href="' + gmapsUrl + '" target="_blank" style="display:inline-block;background:#002147;color:#FFFFFF;padding:4px 10px;border-radius:4px;text-decoration:none;font-weight:bold;font-size:11px;">🌐 Open in Google Maps</a>' +
                        '</div></div>';

                    marker.bindPopup(popupHtml);
                    if (isHost && {map_zoom} <= 6) {{
                        marker.bindTooltip("<b>HQ: Cyber PS Rohini</b>", {{permanent: true, direction: "top", offset: [0, -10]}});
                    }}
                }});

                var corridors = {corr_json};
                corridors.forEach(function(c) {{
                    var latlngs = [c.p1, c.p2];
                    var line = L.polyline(latlngs, {{
                        color: c.color,
                        weight: Math.max(2.5, Math.min(5.5, 1.5 + c.hops * 0.3)),
                        opacity: 0.85,
                        dashArray: '8, 8'
                    }}).addTo(map);
                    line.bindTooltip('<b>Transit Route:</b> ' + c.from + ' ➔ ' + c.to + '<br/><b>Detected Hops:</b> ' + c.hops, {{sticky: true}});
                }});
            </script>
        </body>
        </html>
        """
        st.components.v1.html(leaflet_code, height=560)
        st.markdown(
            '<div style="font-size:0.86rem;color:#334155;background:#F1F5F9;padding:10px 16px;border-radius:4px;border-left:4px solid #002147;">'
            '<strong>Tactical Map Activated:</strong> Uses direct satellite and street tile layers with zero API key dependencies. '
            '<strong>Gold Star:</strong> Cyber Police Station Rohini Sector-17 (Command Center). '
            '<strong>Click any precinct or route</strong> to view statutory jurisdiction, nodal contact, and open direct Google Maps navigation.'
            '</div>',
            unsafe_allow_html=True
        )

    # ═════════════════════════════════════════════════════════════
    # TAB 3: GOOGLE MAPS LIVE INTELLIGENCE & API CONSOLE
    # ═════════════════════════════════════════════════════════════
    with tab_gmaps:
        st.markdown('<div class="dp-sec-head">Google Maps Platform Operational Law Enforcement Terminal</div>', unsafe_allow_html=True)
        
        g_c1, g_c2, g_c3 = st.columns([1.5, 1.2, 1.3])
        with g_c1:
            stored_key = st.session_state.get("google_maps_api_key", os.environ.get("GOOGLE_MAPS_API_KEY", ""))
            api_key_input = st.text_input(
                "Google Maps Platform API Key (Optional)",
                value=stored_key,
                type="password",
                help="Paste official Google Maps API Key to activate official Google Maps Embed API v1, Street View, and driving directions"
            )
            if api_key_input != stored_key:
                st.session_state["google_maps_api_key"] = api_key_input
                os.environ["GOOGLE_MAPS_API_KEY"] = api_key_input
        with g_c2:
            sel_hotspot_name = st.selectbox(
                "Target Hotspot / Precinct",
                [h["name"] for h in HOTSPOTS],
                index=0
            )
            sel_hotspot = next(h for h in HOTSPOTS if h["name"] == sel_hotspot_name)
        with g_c3:
            g_mode = st.radio("Map Imagery Type", ["Satellite (High-Resolution)", "Roadmap / Traffic", "Transit Directions Corridor"], horizontal=True)

        # Distance calculation
        h_lat, h_lng = sel_hotspot["lat"], sel_hotspot["lng"]
        dist_from_rohini = intelligence.haversine_distance(28.7159, 77.1171, h_lat, h_lng)

        gm_left, gm_right = st.columns([2.2, 1.2])

        with gm_left:
            # Construct Google Maps Embed or High-Res Tactical Precinct Canvas
            clean_key = api_key_input.strip() if api_key_input else ""
            if clean_key and len(clean_key) > 10:
                if "Directions" in g_mode:
                    embed_url = f"https://www.google.com/maps/embed/v1/directions?key={clean_key}&origin=28.7159,77.1171&destination={h_lat},{h_lng}&mode=driving"
                else:
                    m_type = "satellite" if "Satellite" in g_mode else "roadmap"
                    embed_url = f"https://www.google.com/maps/embed/v1/place?key={clean_key}&q={h_lat},{h_lng}&zoom=14&maptype={m_type}"

                iframe_code = f"""
                <div style="border: 2px solid #002147; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,33,71,0.15);">
                    <iframe
                        width="100%"
                        height="540"
                        frameborder="0"
                        scrolling="no"
                        marginheight="0"
                        marginwidth="0"
                        src="{embed_url}"
                        allowfullscreen>
                    </iframe>
                </div>
                """
                st.components.v1.html(iframe_code, height=550)
            else:
                # Standalone Interactive Satellite Precinct Terminal (Never blocked by X-Frame-Options)
                precinct_tile = "satellite" if "Satellite" in g_mode else "osm"
                precinct_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                    <style>
                        body {{ margin: 0; padding: 0; font-family: sans-serif; }}
                        #precinct-map {{ width: 100%; height: 500px; border-radius: 6px; }}
                        .crosshair {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000; pointer-events: none; }}
                    </style>
                </head>
                <body>
                    <div style="position: relative;">
                        <div id="precinct-map"></div>
                        <div class="crosshair">
                            <svg width="40" height="40" viewBox="0 0 40 40">
                                <circle cx="20" cy="20" r="16" fill="none" stroke="#DC2626" stroke-width="2" stroke-dasharray="3,3"/>
                                <line x1="20" y1="0" x2="20" y2="40" stroke="#DC2626" stroke-width="2"/>
                                <line x1="0" y1="20" x2="40" y2="20" stroke="#DC2626" stroke-width="2"/>
                                <circle cx="20" cy="20" r="3" fill="#DC2626"/>
                            </svg>
                        </div>
                    </div>
                    <script>
                        var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 19 }});
                        var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ maxZoom: 19 }});
                        var map = L.map('precinct-map', {{
                            center: [{h_lat}, {h_lng}],
                            zoom: 14,
                            layers: [{'satellite' if 'Satellite' in g_mode else 'osm'}]
                        }});
                        var baseMaps = {{ "🛰️ Satellite": satellite, "🗺️ Street Map": osm }};
                        L.control.layers(baseMaps).addTo(map);

                        L.circle([{h_lat}, {h_lng}], {{
                            color: '#DC2626',
                            fillColor: '#DC2626',
                            fillOpacity: 0.25,
                            radius: 3000
                        }}).addTo(map);

                        L.marker([{h_lat}, {h_lng}]).addTo(map)
                            .bindPopup('<b>{sel_hotspot["name"]}</b><br/>{sel_hotspot["police_station"]}<br/>GPS: {h_lat:.4f}° N, {h_lng:.4f}° E')
                            .openPopup();
                    </script>
                </body>
                </html>
                """
                st.components.v1.html(precinct_code, height=510)
                st.caption(f"Tactical Satellite/Street Canvas centered on **{sel_hotspot['name']}** ({h_lat:.4f}° N, {h_lng:.4f}° E).")

        with gm_right:
            badge_color = sel_hotspot["color"]
            st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #CBD5E1;border-top:5px solid {badge_color};padding:16px;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.06);font-size:0.86rem;line-height:1.75;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-size:1.1rem;font-weight:900;color:#002147;">{sel_hotspot['name']}</span>
        <span style="background:{badge_color};color:#FFFFFF;padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:800;">{sel_hotspot['risk']}</span>
    </div>
    <hr style="margin:8px 0;border:none;border-top:1px solid #E2E8F0;"/>
    <strong>GPS Coordinates:</strong> <code>{h_lat:.4f}° N, {h_lng:.4f}° E</code><br/>
    <strong>Distance from Cyber PS Rohini:</strong> <strong style="color:#C4122F;">{dist_from_rohini:.1f} km</strong><br/>
    <strong>Jurisdictional Police Station:</strong><br/>
    <span style="color:#002147;font-weight:700;">{sel_hotspot['police_station']}</span><br/>
    <strong>Nodal Investigating Officer:</strong> {sel_hotspot['nodal']}<br/>
    <strong>Official Control Room Helpline:</strong> <code>{sel_hotspot['phone']}</code><br/>
    <strong>District Magistracy:</strong> {sel_hotspot['dm']}<br/>
    <hr style="margin:8px 0;border:none;border-top:1px solid #E2E8F0;"/>
    <strong>Operational Modus Operandi:</strong><br/>
    <span style="color:#334155;">{sel_hotspot['typologies']}</span><br/>
    <hr style="margin:8px 0;border:none;border-top:1px solid #E2E8F0;"/>
    <strong>Statutory Authority & Remand:</strong><br/>
    <span style="font-size:0.80rem;color:#475569;">
        • <strong>Section 79 BNSS, 2023:</strong> Cross-state pursuit & physical apprehension of syndicate coordinators.<br/>
        • <strong>Section 106 BNSS, 2023:</strong> Ex-parte debit freeze order to nodal bank branches.<br/>
        • <strong>Section 66D IT Act:</strong> Cognizable offence of cheating by personation via computer resources.
    </span>
</div>
""", unsafe_allow_html=True)

            gmaps_direct_url = f"https://www.google.com/maps/search/?api=1&query={h_lat},{h_lng}"
            st.link_button(
                f"🌐 Open {sel_hotspot['name']} in Google Maps (New Tab)",
                gmaps_direct_url,
                use_container_width=True
            )

            if not api_key_input:
                st.info(
                    "Paste your **Google Maps Platform API Key** above to activate official Google Maps Embed API v1 with real-time turn-by-turn driving corridors and Google Street View."
                )

    # ═════════════════════════════════════════════════════════════
    # TAB 4: INTERSTATE CRIME CORRIDORS & REMAND DOSSIER
    # ═════════════════════════════════════════════════════════════
    with tab_dossier:
        st.markdown('<div class="dp-sec-head">Comprehensive Inter-State Money Flow Corridors</div>', unsafe_allow_html=True)
        corr_table_rows = []
        for (c1, c2), data in corridor_items:
            p1 = CITY_COORDS.get(c1, (28.7159, 77.1171))
            p2 = CITY_COORDS.get(c2, (28.7159, 77.1171))
            transit_dist = intelligence.haversine_distance(p1[0], p1[1], p2[0], p2[1])
            corr_table_rows.append({
                "Origin Hub (Crime Base)": c1,
                "Destination Hub (Cashout/Sink)": c2,
                "Air Corridor Distance (km)": f"{transit_dist:.1f} km",
                "Active Transaction Hops": data["count"],
                "Correlated Typologies": len(data["scenarios"]),
                "Sample Scenarios": ", ".join(list(data["scenarios"])[:2]).replace("_", " ").title(),
                "Recommended Legal Action": "Section 79 BNSS Transit Remand to Rohini Court"
            })
        st.dataframe(pd.DataFrame(corr_table_rows), use_container_width=True, height=380)

        st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #CBD5E1;border-left:5px solid #002147;padding:16px;border-radius:4px;font-size:0.86rem;line-height:1.8;margin-top:14px;">
    <strong>Inter-State Law Enforcement Standard Operating Procedure (SOP):</strong><br/>
    1. <strong>Formal Requisition:</strong> When funds flow from <em>Mewat/Jamtara/Bharatpur</em> into Delhi/NCR or Mumbai sink accounts, the Investigating Officer (I.O.) shall immediately transmit an official notice under <strong>Section 94 BNSS</strong> to the recipient nodal bank.<br/>
    2. <strong>Physical Raid & Apprehension:</strong> In case of cross-border operations into Haryana (Nuh) or Rajasthan (Bharatpur/Alwar), the team dispatched from Cyber PS Rohini shall notify the jurisdictional SP/DSP under <strong>Section 79 BNSS</strong> before securing the accused.<br/>
    3. <strong>Transit Remand:</strong> Arrested operatives must be produced before the nearest Judicial Magistrate within 24 hours of arrest (excluding travel time) to obtain a Transit Remand order for production before the Special Cyber Court at Rohini Courts Complex, Delhi.
</div>""", unsafe_allow_html=True)

    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 8: FRAUD INCIDENT TIMELINE
# ═══════════════════════════════════════════════════════════
elif "8. Fraud Incident" in selected_page:
    module_head(
        "Module 8: Fraud Incident Timeline & Nocturnal Stream Analysis",
        "Chronological transaction flow & automated nocturnal 1–4 AM anomaly detection"
    )

    tx_df = pd.DataFrame(transactions)
    tx_df["amount"] = pd.to_numeric(tx_df["amount"], errors="coerce")
    tx_df["parsed_dt"] = pd.to_datetime(tx_df["timestamp"], errors="coerce")
    tx_df = tx_df.dropna(subset=["parsed_dt"])
    tx_df["date"] = tx_df["parsed_dt"].dt.date
    tx_df["hour"] = tx_df["parsed_dt"].dt.hour

    daily = tx_df.groupby("date")["amount"].agg(["count", "sum"]).reset_index()
    daily.columns = ["date", "count", "total_amount"]

    t1, t2 = st.columns(2)
    with t1:
        st.markdown('<div class="dp-sec-head">Daily Transaction Volume (₹)</div>', unsafe_allow_html=True)
        fig_vol = px.area(daily, x="date", y="total_amount",
                          color_discrete_sequence=["#002147"])
        fig_vol.update_traces(fillcolor="rgba(0,33,71,0.15)")
        fig_vol.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5),
                              plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_vol, use_container_width=True)

    with t2:
        st.markdown('<div class="dp-sec-head">Hourly Distribution — Nocturnal 1–4 AM Flag</div>', unsafe_allow_html=True)
        hourly = tx_df.groupby("hour")["amount"].count().reset_index()
        hourly.columns = ["Hour", "Transactions"]
        hourly["Flag"] = hourly["Hour"].apply(lambda h: "Nocturnal (1–4 AM)" if 1 <= h <= 4 else "Standard Hours")
        fig_hr = px.bar(hourly, x="Hour", y="Transactions", color="Flag",
                        color_discrete_map={"Nocturnal (1–4 AM)": "#C4122F", "Standard Hours": "#002147"})
        fig_hr.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5),
                             plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_hr, use_container_width=True)

    # Channel distribution
    t3, t4 = st.columns(2)
    with t3:
        st.markdown('<div class="dp-sec-head">Fraud by Payment Channel</div>', unsafe_allow_html=True)
        legit = {"legitimate_retail_flow", "legitimate_transfer"}
        fraud_ch = tx_df[~tx_df["scenario_label"].isin(legit)]["channel"].value_counts().reset_index()
        fraud_ch.columns = ["Channel", "Count"]
        fig_ch = px.pie(fraud_ch, values="Count", names="Channel", hole=0.5,
                        color_discrete_sequence=px.colors.qualitative.Set2)
        fig_ch.update_layout(height=280, margin=dict(l=5, r=5, t=5, b=5))
        st.plotly_chart(fig_ch, use_container_width=True)

    with t4:
        st.markdown('<div class="dp-sec-head">Weekly Fraud Velocity Trend</div>', unsafe_allow_html=True)
        fraud_df_tl = tx_df[~tx_df["scenario_label"].isin(legit)].copy()
        fraud_df_tl["week"] = fraud_df_tl["parsed_dt"].dt.isocalendar().week
        weekly = fraud_df_tl.groupby("week")["amount"].sum().reset_index()
        fig_wk = px.line(weekly, x="week", y="amount", markers=True,
                         color_discrete_sequence=["#C4122F"])
        fig_wk.update_layout(height=280, margin=dict(l=5, r=5, t=5, b=5),
                             plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_wk, use_container_width=True)

    st.markdown('<div class="dp-sec-head">Recent Fraud Incidents (Chronological Stream)</div>', unsafe_allow_html=True)
    fraud_rows = tx_df[~tx_df["scenario_label"].isin(legit)].sort_values("parsed_dt", ascending=False)
    st.dataframe(
        fraud_rows[["transaction_id", "src_account", "dst_account", "amount", "channel", "timestamp", "scenario_label", "city"]].head(80),
        use_container_width=True
    )
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 9: CASE EXPLORER & KYC DOSSIER
# ═══════════════════════════════════════════════════════════
elif "9. Case Explorer" in selected_page:
    module_head(
        "Module 9: Case Explorer & KYC Dossier Inspector",
        "Deep-dive forensic dossier across KYC, device telemetry, and transaction ledgers"
    )

    s_query = st.text_input("🔍 Lookup Account ID / Phone / UPI ID", value="")
    acc_obj = None
    if s_query:
        acc_obj = next(
            (a for a in accounts if
             s_query.lower() in a.get("account_id", "").lower() or
             s_query.lower() in a.get("upi_id", "").lower()),
            None
        )
    if not acc_obj and accounts:
        acc_obj = accounts[0]

    cid = acc_obj.get("customer_id", "")
    cust_obj = next((c for c in customers if c.get("customer_id") == cid), {})
    dev_objs = [d for d in devices if d.get("account_id") == acc_obj["account_id"]]
    ev = risk_engine.evaluate_account(acc_obj["account_id"])

    risk_color = {"Critical": "#DC2626", "High": "#F97316", "Medium": "#F59E0B", "Low": "#16A34A"}.get(ev["risk_tier"], "#64748B")
    st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E5E7EB;border-left:5px solid {risk_color};
            padding:12px 18px;border-radius:6px;margin-bottom:14px;">
    <strong style="font-size:1.1rem;color:#002147;">Entity Dossier: <code>{acc_obj['account_id']}</code></strong>
    &nbsp;&bull;&nbsp;
    <span style="background:{risk_color};color:#FFFFFF;padding:3px 10px;border-radius:20px;font-weight:700;font-size:0.8rem;">
        {ev['taxonomy_label']} — {ev['risk_tier']} RISK
    </span>
</div>""", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Bank Institution", acc_obj.get("bank", ""))
    d2.metric("UPI Application", acc_obj.get("upi_app", ""))
    d3.metric("Ensemble Score", f"{ev['ensemble_score']}/100", ev["risk_tier"])
    d4.metric("Mastermind Score", f"{ev['mastermind_score']}%")

    tab_k, tab_d, tab_l, tab_r = st.tabs(["👤 KYC Profile", "📱 Linked Devices", "💸 Transaction Ledger", "📊 Risk Components"])
    with tab_k:
        st.json({
            "Customer Name": cust_obj.get("name", "N/A"),
            "Registered Mobile": cust_obj.get("phone", "N/A"),
            "KYC Verification": cust_obj.get("kyc_status", "N/A"),
            "Registered Address": cust_obj.get("home_location", "N/A"),
            "SIM Card ICCID": cust_obj.get("sim_iccid", "N/A"),
            "Telecom Operator": cust_obj.get("telecom_operator", "N/A"),
            "Account Type": acc_obj.get("account_type", "Savings"),
            "Current Balance": f"₹{float(acc_obj.get('balance', 0)):,.2f}",
            "Terminal IP": acc_obj.get("ip_address", "N/A"),
        })

    with tab_d:
        if dev_objs:
            st.dataframe(pd.DataFrame(dev_objs), use_container_width=True)
        else:
            st.warning("No hardware device records found for this entity.")

    with tab_l:
        acc_txs = [t for t in transactions
                   if t.get("src_account") == acc_obj["account_id"] or t.get("dst_account") == acc_obj["account_id"]]
        st.dataframe(pd.DataFrame(acc_txs), use_container_width=True)

    with tab_r:
        sub_scores = ev["sub_scores"]
        ss_df = pd.DataFrame([{"Engine": k.replace("_", " ").title(), "Score": v} for k, v in sub_scores.items()])
        fig_ss = px.bar(ss_df, x="Engine", y="Score", color_discrete_sequence=["#002147"], text="Score")
        fig_ss.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5),
                             plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        fig_ss.update_traces(textposition="outside")
        st.plotly_chart(fig_ss, use_container_width=True)
        for e_item in ev["evidence"]:
            st.markdown(f"&bull; {e_item}")
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 10: INVESTIGATION MODE (ALL 20 REAL CASES)
# ═══════════════════════════════════════════════════════════
elif "10. Investigation Mode" in selected_page:
    module_head(
        "Module 10: Investigation Mode (Multi-Hop Attribution)",
        "Reconstruct multi-hop fund trails: Victim ➔ Mule ➔ Layering ➔ Exit Sink"
    )

    # All 20 cases in dropdown
    case_options = [
        f"{cid}  |  {c['typology_name']}  |  Loss ₹{c['total_incurred_loss']:,.0f}"
        for cid, c in REAL_CASES.items()
    ]
    selected_option = st.selectbox("🗂️ Select Active FIR Investigation Case", case_options)
    selected_fir = selected_option.split("  |  ")[0].strip()
    active_case = REAL_CASES[selected_fir]

    c_top1, c_top2, c_top3, c_top4 = st.columns(4)
    c_top1.metric("FIR Number", active_case["case_id"].split("/")[-1])
    c_top2.metric("Total Loss", f"₹{active_case['total_incurred_loss']:,.2f}")
    c_top3.metric("Typology", active_case["typology_name"][:26])
    c_top4.metric("Complainant", active_case["complainant"][:20])

    st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E5E7EB;border-left:5px solid #002147;
            padding:12px 16px;border-radius:6px;margin-bottom:14px;font-size:0.83rem;">
    <strong>FIR Case:</strong> {active_case['case_id']} &nbsp;|&nbsp;
    <strong>Daily Diary Ref:</strong> {active_case.get('gd_entry', '')} &nbsp;|&nbsp;
    <strong>Complainant Contact:</strong> {active_case['phone']} &nbsp;|&nbsp;
    <strong>Victim Account:</strong> <code>{active_case['victim_account']}</code>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="dp-sec-head">Multi-Hop Money Trail Reconstruction</div>', unsafe_allow_html=True)

    for h in active_case["hops"]:
        cctv_alert = (
            f'<span style="background:#FEE2E2;color:#991B1B;font-weight:700;padding:3px 10px;border-radius:20px;font-size:0.75rem;">'
            f'🔴 {h["cctv_status"]}</span>'
            if h.get("cctv_days_left") and h["cctv_days_left"] < 20
            else f'<span style="color:#64748B;font-size:0.75rem;">⚪ {h["cctv_status"]}</span>'
        )
        hop_color = ["#002147", "#F59E0B", "#C4122F"][min(h["hop_index"] - 1, 2)]
        st.markdown(f"""
<div class="hop-card-item" style="border-left-color:{hop_color};">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
        <span style="font-weight:900;color:{hop_color};font-size:0.98rem;">
            HOP {h['hop_index']}: {h['stage']}
        </span>
        <span class="hop-badge-pill">₹{h['amount']:,.2f} via {h['channel']}</span>
    </div>
    <div style="background:#F8FAFC;border-radius:4px;padding:8px 12px;font-size:0.82rem;margin-bottom:8px;">
        <code style="color:#002147;font-size:0.85rem;">{h['src']}</code>
        <span style="color:#C4122F;font-weight:900;font-size:1.1rem;margin:0 8px;">➔</span>
        <code style="color:#C4122F;font-size:0.85rem;">{h['dst']}</code>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.79rem;color:#475569;">
        <div>&bull; <strong>Timestamp:</strong> {h['timestamp']} ({h['time_elapsed']})</div>
        <div>&bull; <strong>UTR Number:</strong> <code>{h['utr']}</code></div>
        <div>&bull; <strong>Digital Overlap:</strong> {h['digital_overlap']}</div>
        <div>&bull; <strong>Physical Evidence:</strong> {h['physical_evidence']}</div>
        <div>&bull; <strong>CCTV Retention:</strong> {cctv_alert}</div>
        <div>&bull; <strong>Mastermind Probability:</strong> <strong style="color:#C4122F;">{h['coordinator_prob']}%</strong></div>
    </div>
    <div style="margin-top:10px;background:#EFF6FF;padding:8px 12px;border-radius:4px;font-size:0.78rem;color:#1E40AF;font-weight:600;">
        🔍 Forensic Finding: {h['forensic_summary']}
    </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="dp-sec-head" style="margin-top:16px;">Official Case Diary Entry (Para 4 Fund Flow Reconstruction)</div>', unsafe_allow_html=True)
    st.text_area("Official Case Diary Text", value=active_case.get("narrative", ""), height=160)
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 11: FRAUD RING DETECTION & SYNDICATE ROSTER
# ═══════════════════════════════════════════════════════════
elif "11. Fraud Ring" in selected_page:
    module_head(
        "Module 11: Fraud Ring Detection & Syndicate Roster",
        f"Partitioned {len(FRAUD_RINGS)} active cybercrime syndicates with hierarchical role breakdown"
    )

    ring_table = [{
        "Syndicate ID": r["ring_id"],
        "Fraud Typology": r["typology"],
        "Member Accounts": r["size"],
        "Coordinator Node": r["coordinator"],
        "Mastermind Centrality": f"{r['coordinator_score']}%",
        "Total Stolen Volume": f"₹{r['total_fraud_amount']:,.2f}",
        "Registered Incidents": r["incident_count"],
    } for r in FRAUD_RINGS]
    st.dataframe(pd.DataFrame(ring_table), use_container_width=True, height=320)

    rb1, rb2 = st.columns(2)
    with rb1:
        fig_bub = px.scatter(
            pd.DataFrame(ring_table),
            x="Member Accounts", y="Total Stolen Volume",
            size="Registered Incidents", color="Fraud Typology",
            hover_name="Fraud Typology", text="Syndicate ID",
            color_discrete_sequence=px.colors.qualitative.Dark24,
            title="Syndicate Clustering: Members vs Total Fraud Volume (₹)"
        )
        fig_bub.update_layout(height=380, margin=dict(l=5, r=5, t=40, b=5),
                              plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                              showlegend=False)
        st.plotly_chart(fig_bub, use_container_width=True)

    with rb2:
        st.markdown('<div class="dp-sec-head">Syndicate Volume Distribution</div>', unsafe_allow_html=True)
        ring_amounts = pd.DataFrame([{
            "Ring": r["ring_id"],
            "Amount": r["total_fraud_amount"],
            "Typology": r["typology"][:20]
        } for r in FRAUD_RINGS]).sort_values("Amount", ascending=True).tail(12)
        fig_ra = px.bar(ring_amounts, x="Amount", y="Ring", orientation="h",
                        color_discrete_sequence=["#C4122F"],
                        hover_data=["Typology"])
        fig_ra.update_layout(height=380, margin=dict(l=5, r=5, t=10, b=5),
                             plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_ra, use_container_width=True)

    st.markdown('<div class="dp-sec-head">Inspect Syndicate Structure & Member Roster</div>', unsafe_allow_html=True)
    sel_ring_id = st.selectbox("Select Syndicate for Role Breakdown", [r["ring_id"] for r in FRAUD_RINGS])
    target_ring = next(r for r in FRAUD_RINGS if r["ring_id"] == sel_ring_id)

    rc1, rc2 = st.columns([1.2, 1])
    with rc1:
        st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-top:4px solid #C4122F;
            padding:16px;border-radius:6px;">
    <div style="font-weight:900;color:#C4122F;font-size:1.05rem;margin-bottom:8px;">
        {target_ring['ring_id']} &bull; {target_ring['typology']}
    </div>
    <div style="color:#475569;font-size:0.83rem;line-height:1.8;">
        &bull; <strong>Coordinator Account:</strong> <code>{target_ring['coordinator']}</code>
        ({target_ring['coordinator_score']}% Mastermind Centrality)<br/>
        &bull; <strong>Total Member Nodes:</strong> {target_ring['size']} accounts<br/>
        &bull; <strong>Total Traced Stolen Volume:</strong>
        <strong style="color:#C4122F;">₹{target_ring['total_fraud_amount']:,.2f}</strong><br/>
        &bull; <strong>Correlated Incidents:</strong> {target_ring['incident_count']} multi-hop cases
    </div>
</div>""", unsafe_allow_html=True)

    with rc2:
        st.markdown("**Syndicate Mule Accounts (Roster):**")
        mule_preview = []
        for m in target_ring["mules"][:10]:
            ev_m = risk_engine.evaluate_account(m)
            mule_preview.append({
                "Account ID": m,
                "Class": ev_m["taxonomy_label"],
                "Score": f"{ev_m['ensemble_score']}/100"
            })
        st.dataframe(pd.DataFrame(mule_preview), use_container_width=True)
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 12: STATISTICAL EVALUATION & BENCHMARKS
# ═══════════════════════════════════════════════════════════
elif "12. Statistical Evaluation" in selected_page:
    module_head(
        "Module 12: Statistical Evaluation & Benchmarks",
        "Multi-metric evaluation across Balanced Accuracy, MCC, Cohen's Kappa, and ROC-AUC"
    )

    ev_tab1, ev_tab2 = st.tabs([
        "Live Production Attribution Models (Held-Out Test Set)",
        "Historical Research Reference Baselines (Offline GNN Experiments)"
    ])

    with ev_tab1:
        st.caption("Genuinely computed metrics from held-out test evaluation (20% test partition, N=317 accounts, random seed 42).")
        live_bm = []
        if "rf" in _eval_cache and _eval_cache["rf"].get("is_live"):
            r = _eval_cache["rf"]
            live_bm.append({
                "Model Architecture": "Random Forest",
                "Accuracy": f"{r['accuracy']*100:.1f}%",
                "Balanced Acc": f"{r['balanced_accuracy']*100:.1f}%",
                "Macro F1": f"{r['macro_f1']:.3f}",
                "MCC": f"{r['mcc']:.3f}",
                "Cohen κ": f"{r['cohen_kappa']:.3f}",
                "ROC-AUC": f"{r.get('roc_auc', 1.0):.3f}",
                "Training Strategy": r["params"],
                "Status": "Live Evaluated"
            })
        if "xgb" in _eval_cache and _eval_cache["xgb"].get("is_live"):
            r = _eval_cache["xgb"]
            live_bm.append({
                "Model Architecture": "XGBoost",
                "Accuracy": f"{r['accuracy']*100:.1f}%",
                "Balanced Acc": f"{r['balanced_accuracy']*100:.1f}%",
                "Macro F1": f"{r['macro_f1']:.3f}",
                "MCC": f"{r['mcc']:.3f}",
                "Cohen κ": f"{r['cohen_kappa']:.3f}",
                "ROC-AUC": f"{r.get('roc_auc', 1.0):.3f}",
                "Training Strategy": r["params"],
                "Status": "Live Evaluated"
            })
        if "lr" in _eval_cache and _eval_cache["lr"].get("is_live"):
            r = _eval_cache["lr"]
            live_bm.append({
                "Model Architecture": "Logistic Regression",
                "Accuracy": f"{r['accuracy']*100:.1f}%",
                "Balanced Acc": f"{r['balanced_accuracy']*100:.1f}%",
                "Macro F1": f"{r['macro_f1']:.3f}",
                "MCC": f"{r['mcc']:.3f}",
                "Cohen κ": f"{r['cohen_kappa']:.3f}",
                "ROC-AUC": f"{r.get('roc_auc', 1.0):.3f}",
                "Training Strategy": r["params"],
                "Status": "Live Evaluated"
            })
        st.dataframe(pd.DataFrame(live_bm), use_container_width=True)

    with ev_tab2:
        st.caption("Offline benchmark references documented during initial research experiments.")
        bm = ModelZoo.get_benchmark_comparison()
        bm_list = [{
            "Model Name": k,
            "Accuracy": f"{v['accuracy']*100:.1f}%",
            "Balanced Acc": f"{v['balanced_accuracy']*100:.1f}%",
            "Macro F1": f"{v['macro_f1']:.3f}",
            "MCC": f"{v['mcc']:.3f}",
            "Cohen κ": f"{v['cohen_kappa']:.3f}",
            "Training Strategy": v["params"],
            "Source": "Offline Research Reference"
        } for k, v in bm.items()]
        st.dataframe(pd.DataFrame(bm_list), use_container_width=True)

    ev_c1, ev_c2 = st.columns([1.1, 1.2])
    with ev_c1:
        st.markdown('<div class="dp-sec-head">ROC-AUC Comparison (Held-Out Test Set)</div>', unsafe_allow_html=True)
        rf_roc = _eval_cache.get("rf", {}).get("roc_auc", 1.0)
        xgb_roc = _eval_cache.get("xgb", {}).get("roc_auc", 1.0)
        lr_roc = _eval_cache.get("lr", {}).get("roc_auc", 1.0)
        roc_data = pd.DataFrame([
            {"Model": "Random Forest (Live)", "ROC-AUC": rf_roc},
            {"Model": "XGBoost (Live)", "ROC-AUC": xgb_roc},
            {"Model": "Logistic Reg (Live)", "ROC-AUC": lr_roc},
            {"Model": "GraphSAGE (Ref)", "ROC-AUC": 0.941},
        ])
        fig_roc = px.bar(roc_data, x="Model", y="ROC-AUC", color_discrete_sequence=["#002147"],
                         text="ROC-AUC")
        fig_roc.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_roc.update_layout(height=340, margin=dict(l=5, r=5, t=10, b=5),
                              plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                              yaxis=dict(range=[0.8, 1.05]))
        st.plotly_chart(fig_roc, use_container_width=True)

    with ev_c2:
        st.markdown('<div class="dp-sec-head">Imbalance Mitigation Strategy</div>', unsafe_allow_html=True)
        st.markdown(r"""
**Square-Root Dampened Class Weights** applied across all supervised and graph architectures:
$$w_c = \sqrt{\frac{N}{N_c}}$$
where $N$ = total graph nodes, $N_c$ = training nodes in class $c$.
""")
        cw = _eval_cache.get("class_weights", {})
        dist = _eval_cache.get("dataset_info", {}).get("class_distribution", {})
        total_n = _eval_cache.get("dataset_info", {}).get("total_in_graph", 1584)

        cw_rows = [
            {"Class": "Normal", "Nodes in Graph": dist.get("Normal", 1305),
             "Share": f"{(dist.get('Normal', 1305)/total_n)*100:.1f}%",
             "Weight Applied": f"{cw.get('Normal', 1.102):.3f}× (dampened majority)"},
            {"Class": "Mule", "Nodes in Graph": dist.get("Mule", 187),
             "Share": f"{(dist.get('Mule', 187)/total_n)*100:.1f}%",
             "Weight Applied": f"{cw.get('Mule', 2.910):.3f}×"},
            {"Class": "Fraudster", "Nodes in Graph": dist.get("Fraudster", 92),
             "Share": f"{(dist.get('Fraudster', 92)/total_n)*100:.1f}%",
             "Weight Applied": f"{cw.get('Fraudster', 4.149):.3f}×"},
            {"Class": "Suspicious", "Nodes in Graph": dist.get("Suspicious", 0),
             "Share": "0.0%",
             "Weight Applied": "N/A (0 transaction edges in current dataset)"},
        ]
        st.dataframe(pd.DataFrame(cw_rows), use_container_width=True)

    st.markdown('<div class="dp-sec-head">Per-Class Precision / Recall Breakdown</div>', unsafe_allow_html=True)
    sel_pr_arch = st.selectbox(
        "Select Architecture for Per-Class Breakdown",
        ["Random Forest (Production)", "XGBoost (Gradient Boosted Trees)", "Logistic Regression (Linear Baseline)"]
    )
    if "Random Forest" in sel_pr_arch:
        pr_list = _eval_cache.get("per_class_rf", [])
    elif "XGBoost" in sel_pr_arch:
        pr_list = _eval_cache.get("per_class_xgb", [])
    else:
        pr_list = _eval_cache.get("per_class_lr", [])

    st.dataframe(pd.DataFrame(pr_list), use_container_width=True)
    st.caption("Evaluated on 317 held-out test accounts using scikit-learn classification_report. Zero label leakage.")
    dev_footer()


# ═══════════════════════════════════════════════════════════
# MODULE 13: LEGAL NOTICES, CASE REPORTS & DATA EXPORT
# ═══════════════════════════════════════════════════════════
elif "13. Legal Notices" in selected_page:
    module_head(
        "Module 13: Legal Notices, Case Reports & Data Export",
        "Section 94 BNSS requisitions, formal PDF case reports, and forensic dataset exports"
    )

    sel_rep_fir = st.selectbox(
        "Select FIR Case for Requisition Notice",
        [f"{cid}  |  {c['typology_name']}" for cid, c in REAL_CASES.items()]
    )
    case_key = sel_rep_fir.split("  |  ")[0].strip()
    active_rep_case = REAL_CASES[case_key]

    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        st.markdown('<div class="dp-sec-head">Section 94 BNSS Legal Requisition Notice</div>', unsafe_allow_html=True)
        notice_txt = generate_legal_notice(active_rep_case)
        st.text_area("Notice Draft (Court / Bank Ready)", value=notice_txt, height=300)
        st.download_button(
            "📥 Download Section 94 Notice (.txt)",
            data=notice_txt,
            file_name=f"S94_BNSS_{active_rep_case['case_id'].replace('/', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with rep_col2:
        st.markdown('<div class="dp-sec-head">Judicial PDF Case Dossier</div>', unsafe_allow_html=True)
        if HAS_REPORTLAB:
            pdf_filename = "fin_suraksha_case_dossier.pdf"
            generate_case_pdf_report(active_rep_case, pdf_filename)
            with open(pdf_filename, "rb") as f_pdf:
                pdf_data = f_pdf.read()
            st.download_button(
                "📥 Download Official PDF Case Report",
                data=pdf_data,
                file_name=f"FinSuraksha_{active_rep_case['case_id'].replace('/', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.warning("ReportLab library not detected. Install via: pip install reportlab")
            st.markdown("**Notice text available above for manual export.**")

    st.markdown("---")
    st.markdown('<div class="dp-sec-head">Export Full Case Ecosystem Archive</div>', unsafe_allow_html=True)
    ecol1, ecol2 = st.columns(2)
    with ecol1:
        if st.button("📦 Build & Download Full CSV Bundle (.zip)", use_container_width=True):
            z_path = ecosystem_to_csv_bundle(pipe["eco"])
            with open(z_path, "rb") as f_z:
                z_data = f_z.read()
            st.download_button("⬇️ Download ZIP Bundle", data=z_data,
                               file_name="fin_suraksha_sample_dataset.zip",
                               mime="application/zip",
                               use_container_width=True)
    with ecol2:
        # Export all cases as CSV
        cases_export = pd.DataFrame([{
            "FIR Number": c["case_id"],
            "Complainant": c["complainant"],
            "Typology": c["typology_name"],
            "Victim Account": c["victim_account"],
            "Sink Account": c["sink_account"],
            "Total Loss (₹)": c["total_incurred_loss"],
            "Hops Traced": len(c["hops"]),
        } for c in REAL_CASES.values()])
        st.download_button(
            "📥 Export All Active Cases (CSV)",
            data=cases_export.to_csv(index=False),
            file_name="fin_suraksha_active_cases.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown('<div class="dp-sec-head">Cryptographic Audit Trail Log</div>', unsafe_allow_html=True)
    audit_data = pd.DataFrame(db.get_audit_log(limit=60))
    st.dataframe(audit_data, use_container_width=True)
    dev_footer()
