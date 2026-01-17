import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# --- GLOBAL CSS (Specific to prevent overrides) ---
st.markdown("""
    <style>
    /* Force main background and text colors */
    .stApp { background-color: white !important; }
    
    /* Ensure Development Name (H1) is visible and black */
    h1 { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        padding-top: 0px !important;
        margin-bottom: 10px !important;
    }

    /* Metric Alignment & Styling */
    [data-testid="stMetric"] {
        text-align: left !important;
    }
    [data-testid="stMetricLabel"] { 
        color: #444444 !important; 
        font-weight: 700 !important; 
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricValue"] { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        font-size: 2.2rem !important;
    }

    /* Sidebar Restoration */
    section[data-testid="stSidebar"] { 
        background-color: #f1f3f6 !important; 
    }
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Input Box Visibility */
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.markdown("### Property Details")
    dev_name = st.text_input("Development / Address", "")
    unit_no  = st.text_input("Unit Number", "")
    sqft     = st.number_input("Size (sqft)", value=None, step=1)
    u_type   = st.text_input("Unit Type", "")
    prepared_by = st.text_input("Prepared By", "")
    
    st.markdown("---")
    st.markdown("### Market Details")
    t_low  = st.number_input("Lowest Transacted (PSF)", value=None, step=1)
    t_high = st.number_input("Highest Transacted (PSF)", value=None, step=1)
    a_low  = st.number_input("Lowest Asking (PSF)", value=None, step=1)
    a_high = st.number_input("Highest Asking (PSF)", value=None, step=1)

    st.markdown("---")
    st.markdown("### Pricing Data")
    fmv      = st.number_input("Fair Market Value (PSF)", value=None, step=1)
    our_ask  = st.number_input("Our Asking (PSF)", value=None, step=1)

# --- CALCULATIONS ---
has_data = all(v is not None and v > 0 for v in [fmv, our_ask, t_high, a_high])
valid_sqft = sqft is not None and sqft > 0

if has_data:
    lower_5, upper_5 = fmv * 0.95, fmv * 1.05
    lower_10, upper_10 = fmv * 0.90, fmv * 1.10
    diff_pct = (our_ask - fmv) / fmv
    status_text, status_color = ("WITHIN 5% OF FMV", "#2ecc71") if abs(diff_pct) <= 0.05 else \
                                ("BETWEEN 5-10% OF FMV", "#f1c40f") if abs(diff_pct) <= 0.10 else \
                                ("MORE THAN 10% OF FMV", "#e74c3c")
else:
    status_text, status_color, diff_pct = "Awaiting Input", "#7f8c8d", 0

tz_sg = timezone(timedelta(hours=8))
today_date = datetime.now(tz_sg).strftime("%d/%m/%Y")

# --- MAIN DASHBOARD ---
st.title(f"{dev_name if dev_name else 'Market Analysis'}")

# Row 1: PSF Metrics (Left-Weighted)
m1, m2, m3, m4 = st.columns([1.2, 1.2, 1.2, 2])
m1.metric("Est FMV (PSF)", f"${fmv:,.0f} PSF" if fmv else "-")
m2.metric("Our Asking (PSF)", f"${our_ask:,.0f} PSF" if our_ask else "-")
m3.metric("PSF Variance", f"{diff_pct:+.1%}" if has_data else "-")

# Row 2: Quantum Metrics
q1, q2, q3, q4 = st.columns([1.2, 1.2, 1.2, 2])
q1.metric("Est FMV (Quantum)", f"${(fmv * sqft):,.0f}" if (fmv and valid_sqft) else "-")
q2.metric("Our Asking (Quantum)", f"${(our_ask * sqft):,.0f}" if (our_ask and valid_sqft) else "-")

st.divider()

# --- PLOTTING ---
if has_data:
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('white')

    # Shaded Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # Variance Labels (Horizontal & Staggered)
    y_high, y_low = -0.9, -1.3
    ax.text(lower_10, y_high, f"-10%\n${lower_10:,.0f}", ha='center', fontsize=10, weight='bold', color='#7f8c8d')
    ax.text(lower_5, y_low, f"-5%\n${lower_5:,.0f}", ha='center', fontsize=10, weight='bold', color='#7f8c8d')
    ax.text(upper_5, y_high, f"+5%\n${upper_5:,.0f}", ha='center', fontsize=10, weight='bold', color='#7f8c8d')
    ax.text(upper_10, y_low, f"+10%\n${upper_10:,.0f}", ha='center', fontsize=10, weight='bold', color='#7f8c8d')

    # Lines & Data
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=8, linewidth=5)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=8, linewidth=5)

    data_min = min(t_low, a_low, lower_10)
    data_max = max(t_high, a_high, upper_10)

    # Side labels - Positioned to align with Title
    ax.text(data_min - 15, 2, 'TRANSACTED PSF', weight='bold', ha='right', va='center', fontsize=11)
    ax.text(data_min - 15, 1, 'CURRENT ASKING PSF', weight='bold', ha='right', va='center', fontsize=11)

    # Points
    ax.scatter(fmv, 2, color='black', s=150, zorder=5)
    ax.plot([fmv, fmv], [2, 0.4], color='#bdc3c7', linestyle='--', alpha=0.5)
    ax.scatter(our_ask, 1, color=status_color, s=250, edgecolors='black', zorder=6)
    ax.plot([our_ask, our_ask], [1, -0.1], color=status_color, linestyle='--', linewidth=2)

    # Property Box (Top Right)
    box_txt = f"Unit: {unit_no}\nSize: {sqft} sqft\nType: {u_type}\nBy: {prepared_by}\nDate: {today_date}"
    ax.text(0.98, 0.82, box_txt, transform=ax.transAxes, ha='right', va='top', fontsize=10, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='#cccccc', boxstyle='round,pad=0.8'))

    # Logo
    if os.path.exists("logo.png"):
        logo_ax = fig.add_axes([0.82, 0.84, 0.14, 0.08]) 
        logo_ax.imshow(mpimg.imread("logo.png"))
        logo_ax.axis('off')

    # Status
    ax.text((data_min + data_max)/2, 2.7, f"STATUS: {status_text}", fontsize=22, weight='bold', color=status_color, ha='center')
    ax.text(fmv, 0.2, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=11)
    ax.text(our_ask, -0.4, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=12)

    ax.axis('off')
    ax.set_ylim(-1.8, 3.5)
    ax.set_xlim(data_min - 250, data_max + 100)

    st.pyplot(fig)
