import streamlit as st
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime, timedelta, timezone
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="CMA Tool", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- CSS: V2.9 (FORCE LIGHT THEME & CONSISTENCY) ---
st.markdown("""
    <style>
    /* 1. GLOBAL THEME OVERRIDE (Force Light Mode) */
    :root {
        --primary-color: #ff4b4b;
        --background-color: #ffffff;
        --secondary-background-color: #f0f2f6;
        --text-color: #000000;
        --font: "Helvetica", sans-serif;
    }
    
    /* Force browser to render standard controls (scrollbars, inputs) in light mode */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        color-scheme: light; 
    }
    
    /* 2. Main App Background -> White */
    .stApp { background-color: white !important; }
    
    /* 3. Global Text -> Black */
    h1, h2, h3, p, div, label, span, .stMetric label, [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* 4. Sidebar -> Consistent Light Grey/White */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* 5. Inputs -> Light Grey Background, Black Text, standard Light Mode Borders */
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stNumberInput input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Labels in sidebar */
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }

    /* Download Button Style */
    div.stDownloadButton > button {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        width: 100%;
    }

    /* 6. Header Management */
    /* Hide Decoration & Toolbar */
    [data-testid="stDecoration"], [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Force Header to be visible but White */
    [data-testid="stHeader"] {
        background-color: white !important;
        border-bottom: 1px solid #e0e0e0;
        z-index: 10 !important;
    }

    /* 7. SIDEBAR TOGGLE BUTTON (High Contrast Black) */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        z-index: 999999 !important;
        
        /* Visible BLACK box */
        background-color: #000000 !important;
        border-radius: 8px !important;
        padding: 4px !important;
        
        margin-top: 10px !important;
        margin-left: 10px !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] button {
        border: none !important;
        background: transparent !important;
        color: white !important;
    }

    /* Force Icon White */
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] i {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
    }

    /* Hide Footer */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CALLBACK FUNCTIONS ---
def calc_fmv_quantum():
    if st.session_state.sqft and st.session_state.fmv_psf:
        st.session_state.fmv_quantum = st.session_state.fmv_psf * st.session_state.sqft

def calc_fmv_psf():
    if st.session_state.sqft and st.session_state.fmv_quantum:
        st.session_state.fmv_psf = st.session_state.fmv_quantum / st.session_state.sqft

def calc_ask_quantum():
    if st.session_state.sqft and st.session_state.ask_psf:
        st.session_state.ask_quantum = st.session_state.ask_psf * st.session_state.sqft

def calc_ask_psf():
    if st.session_state.sqft and st.session_state.ask_quantum:
        st.session_state.ask_psf = st.session_state.ask_quantum / st.session_state.sqft

# --- SIDEBAR INPUTS ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.markdown("### Property Details")
    dev_name = st.text_input("Development / Address", "")
    unit_no  = st.text_input("Unit", "")
    sqft = st.number_input("Size (sqft)", value=None, step=1, key="sqft")
    u_type   = st.text_input("Type", "")
    prepared_by = st.text_input("Agent Name", "")
    
    st.markdown("---")
    
    st.markdown("### Market Data (PSF)")
    t1 = st.number_input("Lowest Transacted (PSF)", value=None, step=0.1, format="%.1f")
    t2 = st.number_input("Highest Transacted (PSF)", value=None, step=0.1, format="%.1f")
    
    if t1 is not None and t2 is not None:
        t_low, t_high = min(t1, t2), max(t1, t2)
    else:
        t_low, t_high = 0, 0
    
    a1 = st.number_input("Lowest Asking (PSF)", value=None, step=0.1, format="%.1f")
    a2 = st.number_input("Highest Asking (PSF)", value=None, step=0
