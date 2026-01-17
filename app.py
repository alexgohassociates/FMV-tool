import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    
    /* Header & Sidebar Visibility */
    h1 { color: #000000 !important; font-weight: 800 !important; }
    section[data-testid="stSidebar"] { background-color: #f1f3f6 !important; }
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Input Boxes: Light Grey with Solid Black Text */
    .stTextInput input, .stNumberInput input {
        background-color: #f1f3f6 !important; 
        color: #000000 !important; 
        border: 1px solid #d1d5db !important;
        font-weight: 600 !important;
    }

    /* Metrics Alignment */
    [data-testid="stMetricValue"] { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        font-size: 2rem !important;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR INPUTS ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("### Property Details")
    dev_name = st.text_input("Development / Address", "Kent Ridge Hill Residences")
    unit_no  = st.text_input("Unit Number", "")
    sqft     = st.number_input("Size (sqft)", value=None, step=1)
    u_type   = st.text_input("Unit Type", "")
    prepared_by = st.text_input("Prepared By", "")
    
    st.markdown("---")
    st.markdown("### Market Details")
    t_low, t_high = st.number_input("Low Transacted", value=None), st.number_input("High Transacted", value=None)
    a_low, a_high = st.number_input("Low Asking", value=None), st.number_input("High Asking", value=None)
    fmv, our_ask = st.number_input("Fair Market Value", value=None), st.number_input("Our Asking", value=None)

# --- CALCULATIONS ---
has_data = all(v is not None and v > 0 for v in [fmv, our_ask, t_high, a_high])
valid_sqft = sqft is not None and sqft > 0
tz_sg = timezone(timedelta(hours=8))
today_date = datetime.now(tz_sg).strftime("%d/%m/%Y")

if has_data:
    lower_5, upper_5 = fmv * 0.95, fmv * 1.05
    lower_10, upper_10 = fmv * 0.90, fmv * 1.10
    diff_pct = (our_ask - fmv) / fmv
    status_text, status_color = ("WITHIN 5% OF FMV", "#2ecc71") if abs(diff_pct) <= 0.05 else \
                                ("BETWEEN 5-10% OF FMV", "#f1c40f") if abs(diff_pct) <= 0.10 else \
                                ("MORE THAN 10% OF FMV", "#e74c3c")
else:
    status_text, status_color, diff_pct = "Awaiting Input", "#7f8c8d", 0

# --- DASHBOARD TOP ---
st.title(f"{dev_name}")
m1, m2, m3, _ = st.columns([2, 2, 2, 4])
m1.metric("Est FMV (PSF)", f"${fmv:,.0f} PSF" if fmv else "-")
m2.metric("Our Asking (PSF)", f"${our_ask:,.0f} PSF" if our_ask else "-")
m3.metric("Variance", f"{diff_pct:+.1%}" if has_data else "-")

q1, q2, _ = st.columns([2, 2, 6])
q1.metric("Est FMV (Quantum)", f"${(fmv * sqft):,.0f}" if (fmv and valid_sqft) else "-")
q2.metric("Our Asking (Quantum)", f"${(our_ask * sqft):,.0f}" if (our_ask and valid_sqft) else "-")
st.divider()

# --- THE CHART ---
if has_data:
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('white')
    # Create room at the top for the aligned header elements
    fig.subplots_adjust(top=0.85) 

    # Plotting Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # Zone Labels (bottom)
    y_vals = [-1.0, -1.4]
    ax.text(lower_10, y_vals[0], f"-10%\n${lower_10:,.0f}", ha='center', fontsize=9, weight='bold', color='#7f8c8d')
    ax.text(lower_5, y_vals[1], f"-5%\n${lower_5:,.0f}", ha='center', fontsize=9, weight='bold', color='#7f8c8d')
    ax.text(upper_5, y_vals[0], f"+5%\n${upper_5:,.0f}", ha='center', fontsize=9, weight='bold', color='#7f8c8d')
    ax.text(upper_10, y_vals[1], f"+10%\n${upper_10:,.0f}", ha='center', fontsize=9, weight='bold', color='#7f8c8d')

    # Data Lines
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=8, linewidth=5)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=8, linewidth=5)

    data_min, data_max = min(t_low, a_low, lower_10), max(t_high, a_high, upper_10)
    ax.text(data_min - 50, 2, 'TRANSACTED PSF', weight='bold', ha='right', va='center', fontsize=11)
    ax.text(data_min - 50, 1, 'CURRENT ASKING PSF', weight='bold', ha='right', va='center', fontsize=11)

    # Main Status Title
    ax.text((data_min + data_max)/2, 2.8, f"STATUS: {status_text}", fontsize=24, weight='bold', color=status_color, ha='center')

    # Aligned Top Header (Logo + Box)
    # 1. Add Logo
    if os.path.exists("logo.png"):
        logo_ax = fig.add_axes([0.82, 0.88, 0.14, 0.08]) # Top Right
        logo_ax.imshow(mpimg.imread("logo.png"))
        logo_ax.axis('off')

    # 2. Add Property Details Box (Perfectly aligned with logo Y-axis)
    info_str = f"Dev: {dev_name} | Unit: {unit_no} | Size: {sqft} sqft | Type: {u_type}\nPrepared By: {prepared_by} | Date: {today_date}"
    ax.text(0.78, 0.94, info_str, transform=fig.transFigure, ha='right', va='top', fontsize=11, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='#cccccc', boxstyle='round,pad=0.6'))

    # FMV/Ask Markers
    ax.scatter(fmv, 2, color='black', s=150, zorder=5)
    ax.text(fmv, 0.3, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=11)
    ax.scatter(our_ask, 1, color=status_color, s=250, edgecolors='black', zorder=6)
    ax.text(our_ask, -0.4, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=12)

    ax.axis('off')
    ax.set_ylim(-1.8, 3.5)
    ax.set_xlim(data_min - 250, data_max + 100)
    st.pyplot(fig)
