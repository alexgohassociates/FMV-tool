import streamlit as st
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime, timedelta, timezone
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# --- CSS: PERFECT "CLEAN" THEME & EQUAL SPACING ---
st.markdown("""
    <style>
    /* 1. Main App Background -> White */
    .stApp { background-color: white !important; }
    
    /* 2. Global Text -> Black & Helvetica */
    h1, h2, h3, p, div, label, .stMetric label, [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* 3. Sidebar -> White */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }

    /* 4. Sidebar Inputs -> Light Grey Box with Black Text */
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stNumberInput input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        border-color: #d1d5db !important;
    }
    
    /* 5. Sidebar Labels -> Black */
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        margin-bottom: 2px !important; /* Tighten label to input */
    }

    /* 6. DOWNLOAD BUTTON -> Match Input Fields */
    div.stDownloadButton > button {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        width: 100%;
    }
    div.stDownloadButton > button:hover {
        background-color: #e5e7eb !important;
        border-color: #9ca3af !important;
        color: #000000 !important;
    }

    /* 7. EQUAL SPACING FIX */
    /* Remove default Streamlit vertical gaps and set our own */
    [data-testid="stSidebar"] .stElementContainer {
        margin-bottom: 0.8rem !important; /* Standard gap between every item */
    }
    /* Tighten up the headers so they don't have huge gaps above them */
    [data-testid="stSidebar"] h3 {
        padding-top: 0.5rem !important;
        padding-bottom: 0.2rem !important;
        margin-bottom: 0 !important;
    }
    /* Adjust the divider line to float exactly in the middle of the gap */
    [data-testid="stSidebar"] hr {
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR INPUTS ---
with st.sidebar:
    # 1. Branding (Logo on Sidebar Top)
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    # 2. Property Details
    st.markdown("### Property Details")
    dev_name = st.text_input("Development / Address", "Kent Ridge Hill Residences")
    unit_no  = st.text_input("Unit", "02-57")
    sqft     = st.number_input("Size (sqft)", value=1079)
    u_type   = st.text_input("Type", "3 Bedroom Premium")
    prepared_by = st.text_input("Agent Name", "James Koh")
    
    st.markdown("---")
    
    # 3. Market Data
    st.markdown("### Market Data")
    t1, t2 = st.number_input("Lowest Transacted (PSF)", value=1000), st.number_input("Highest Transacted (PSF)", value=1200)
    t_low, t_high = min(t1, t2), max(t1, t2)
    
    a1, a2 = st.number_input("Lowest Asking (PSF)", value=1100), st.number_input("Highest Asking (PSF)", value=1300)
    a_low, a_high = min(a1, a2), max(a1, a2)
    
    st.markdown("### Valuation")
    fmv = st.number_input("FMV (PSF)", value=1050)
    our_ask = st.number_input("Asking Price (PSF)", value=1100)

# --- CALCULATIONS ---
has_data = all(v is not None and v > 0 for v in [fmv, our_ask, t_high, a_high])
tz_sg = timezone(timedelta(hours=8))
today_date = datetime.now(tz_sg).strftime("%d %b %Y")

if has_data:
    lower_5, upper_5 = fmv * 0.95, fmv * 1.05
    lower_10, upper_10 = fmv * 0.90, fmv * 1.10
    diff_pct = (our_ask - fmv) / fmv
    
    # Quantum Calculations
    fmv_quantum = fmv * sqft
    ask_quantum = our_ask * sqft
    
    # Dynamic styling based on variance
    if abs(diff_pct) <= 0.05:
        status_text = "Within +/- 5%"
        status_color = "#2ecc71" # Green
    elif abs(diff_pct) <= 0.10:
        status_text = "Between 5 to 10%"
        status_color = "#f1c40f" # Yellow
    else:
        status_text = "Greater than 10%"
        status_color = "#e74c3c" # Red
else:
    status_text, status_color, diff_pct = "Waiting for Data...", "#7f8c8d", 0
    fmv_quantum, ask_quantum = 0, 0

# --- DASHBOARD LAYOUT ---
# Title
st.title(f"{dev_name}")
st.caption(f"Unit: {unit_no} | Size: {sqft:,} sqft | Type: {u_type}")

# Row 1: PSF Metrics & Variance
c1, c2, c3 = st.columns(3)
c1.metric("FMV (PSF)", f"${fmv:,.0f} psf")
c2.metric("Asking (PSF)", f"${our_ask:,.0f} psf")
c3.metric("Variance", f"{diff_pct:+.1%}", delta_color="inverse")

# Row 2: Quantum Metrics
c4, c5, c6 = st.columns(3) 
c4.metric("FMV (Quantum)", f"${fmv_quantum:,.0f}")
c5.metric("Asking (Quantum)", f"${ask_quantum:,.0f}")

st.divider()

# --- PLOTTING ENGINE ---
fig = None

if has_data:
    # Create Figure
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('white')
    
    # Dynamic limits to prevent text cutoff
    all_values = [t_low, t_high, a_low, a_high, fmv, our_ask, lower_10, upper_10]
    data_min = min(all_values)
    data_max = max(all_values)
    data_range = data_max - data_min
    padding = data_range * 0.25 

    # 1. Shaded Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)  # Yellow zone
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.15)  # Green zone
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)  # Yellow zone

    # 2. Zone Labels
    y_labels = -1.5
    style_dict = dict(ha='center', va='top', fontsize=10, weight='bold', color='#95a5a6')
    ax.text(lower_5, y_labels, f"-5%\n${lower_5:,.0f}", **style_dict)
    ax.text(upper_5, y_labels, f"+5%\n${upper_5:,.0f}", **style_dict)
    ax.text(lower_10, y_labels - 0.7, f"-10%\n${lower_10:,.0f}", **style_dict)
    ax.text(upper_10, y_labels - 0.7, f"+10%\n${upper_10:,.0f}", **style_dict)

    # 3. Market Range Lines (Dumbbell Plot)
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=12, linewidth=8, solid_capstyle='round')
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=12, linewidth=8, solid_capstyle='round')

    # 4. Labels for Lines
    text_x_pos = data_min - (data_range * 0.05) 
    ax.text(text_x_pos, 2, 'RECENT TRANSACTED', weight='bold', ha='right', va='center', fontsize=12, color='#3498db')
    ax.text(text_x_pos, 1, 'CURRENT ASKING', weight='bold', ha='right', va='center', fontsize=12, color='#34495e')

    # 5. The "Status" Banner
    ax.text((data_min + data_max)/2, 3.5, f"STATUS: {status_text}", fontsize=24, weight='bold', color='black', ha='center',
            bbox=dict(facecolor='white', edgecolor=status_color, boxstyle='round,pad=0.5', linewidth=2))

    # 6. FMV vs Ask Markers
    ax.scatter(fmv, 2, color='black', s=250, zorder=10, marker='D') 
    ax.text(fmv, 2.4, f"VALUATION\n${fmv:,.0f}", ha="center", weight="bold", fontsize=11)
    
    ax.scatter(our_ask, 1, color=status_color, s=400, edgecolors='black', zorder=11, linewidth=2)
    ax.text(our_ask, 0.4, f"YOUR ASK\n${our_ask:,.0f}", ha="center", weight="bold", color=status_color, fontsize=13)

    # 7. Logo on Graph
    if os.path.exists("logo.png"):
        try:
            logo_img = Image.open("logo.png")
            logo_ax = fig.add_axes([0.75, 0.85, 0.15, 0.12]) 
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')
        except:
            pass 

    # Footer Info
    info_str = (f"{dev_name} ({unit_no}) | {sqft:,} sqft | {u_type}\n"
                f"Analysis by {prepared_by} | {today_date}")
    
    ax.text(0.02, 0.95, info_str, transform=fig.transFigure, ha='left', va='top', fontsize=12, fontweight='bold',
            color='#555555', bbox=dict(facecolor='#f8f9fa', edgecolor='none', boxstyle='round,pad=0.5'))

    # Final visual tweaks
    ax.axis('off')
    ax.set_ylim(-3.0, 5.0)
    ax.set_xlim(data_min - padding, data_max + (padding*0.5))
    
    st.pyplot(fig)

# --- SIDEBAR DOWNLOAD BUTTON ---
with st.sidebar:
    st.markdown("---")
    if fig is not None:
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        st.download_button(
            label="📥 Download Chart for PDF",
            data=img_buffer,
            file_name=f"{dev_name}_Analysis.png",
            mime="image/png",
            use_container_width=True
        )
