import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# --- FORCE VISIBILITY CSS ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; }

    /* Force all text in sidebar and main dashboard to be black */
    h1, h2, h3, p, label, .stMetric label, [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    section[data-testid="stSidebar"] h3 { color: #000000 !important; }

    /* Input Boxes: Grey background with Black Text */
    .stTextInput input, .stNumberInput input {
        background-color: #f1f3f6 !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        font-weight: 600 !important;
    }

    /* Metric Labels Styling */
    [data-testid="stMetricLabel"] p {
        color: #444444 !important;
        font-size: 1rem !important;
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
    unit_no  = st.text_input("Unit Number", "02-57")
    sqft     = st.number_input("Size (sqft)", value=1079)
    u_type   = st.text_input("Unit Type", "3 Bedroom Premium")
    prepared_by = st.text_input("Prepared By", "James Koh")
    
    st.markdown("---")
    st.markdown("### Market Details")
    t_low  = st.number_input("Lowest Transacted (PSF)", value=1000)
    t_high = st.number_input("Highest Transacted (PSF)", value=1200)
    a_low  = st.number_input("Lowest Asking (PSF)", value=1100)
    a_high = st.number_input("Highest Asking (PSF)", value=1300)
    fmv    = st.number_input("Fair Market Value (PSF)", value=1050)
    our_ask = st.number_input("Our Asking (PSF)", value=1100)

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

# --- MAIN DASHBOARD ---
st.title(f"{dev_name}")

col1, col2, col3 = st.columns([3, 3, 3])
col1.metric("Est FMV (PSF)", f"${fmv:,.0f} PSF" if fmv else "-")
col2.metric("Our Asking (PSF)", f"${our_ask:,.0f} PSF" if our_ask else "-")
col3.metric("PSF Variance", f"{diff_pct:+.1%}" if has_data else "-")

col4, col5, _ = st.columns([3, 3, 3])
col4.metric("Est FMV (Quantum)", f"${(fmv * sqft):,.0f}" if (fmv and valid_sqft) else "-")
col5.metric("Our Asking (Quantum)", f"${(our_ask * sqft):,.0f}" if (our_ask and valid_sqft) else "-")

st.divider()

# --- PLOTTING ---
if has_data:
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('white')
    
    # Push the plot down to make room for the horizontal bar
    fig.subplots_adjust(top=0.82) 

    # Plot Background Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # Market Data Lines
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=10, linewidth=6)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=10, linewidth=6)

    data_min, data_max = min(t_low, a_low, lower_10), max(t_high, a_high, upper_10)
    ax.text(data_min - 60, 2, 'TRANSACTED PSF', weight='bold', ha='right', va='center', fontsize=12)
    ax.text(data_min - 60, 1, 'CURRENT ASKING PSF', weight='bold', ha='right', va='center', fontsize=12)

    # Main Status Header
    ax.text((data_min + data_max)/2, 3.0, f"STATUS: {status_text}", fontsize=26, weight='bold', color=status_color, ha='center')

    # --- THE HORIZONTAL DETAILS BAR (Top Aligned) ---
    info_bar = (f"Dev: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}\n"
                f"Prepared By: {prepared_by}  |  Date: {today_date}")
    
    # Positioned at the top-left, matching the logo height
    ax.text(0.02, 0.96, info_bar, transform=fig.transFigure, ha='left', va='top', fontsize=11, fontweight='bold',
            linespacing=1.6, bbox=dict(facecolor='white', edgecolor='#dddddd', boxstyle='round,pad=0.6'))

    # Logo (Top Right)
    if os.path.exists("logo.png"):
        logo_ax = fig.add_axes([0.82, 0.88, 0.14, 0.08]) 
        logo_ax.imshow(mpimg.imread("logo.png"))
        logo_ax.axis('off')

    # PSF Value Labels
    ax.scatter(fmv, 2, color='black', s=200, zorder=10)
    ax.text(fmv, 0.3, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=12)
    ax.scatter(our_ask, 1, color=status_color, s=300, edgecolors='black', zorder=11)
    ax.text(our_ask, -0.5, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=14)

    # Final Styling
    ax.axis('off')
    ax.set_ylim(-2.0, 4.0)
    ax.set_xlim(data_min - 300, data_max + 150)
    st.pyplot(fig)
