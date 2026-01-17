import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# --- CSS: FORCE BLACK TEXT ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, label, .stMetric label, [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("### Property Details")
    dev_name = st.text_input("Development", "Kent Ridge Hill Residences")
    unit_no  = st.text_input("Unit", "02-57")
    sqft     = st.number_input("Size", value=1079)
    u_type   = st.text_input("Type", "3 Bedroom Premium")
    prepared_by = st.text_input("By", "James Koh")
    
    st.markdown("---")
    st.markdown("### Market Details")
    t_low, t_high = st.number_input("Low Transacted", value=1000), st.number_input("High Transacted", value=1200)
    a_low, a_high = st.number_input("Low Asking", value=1100), st.number_input("High Asking", value=1300)
    fmv, our_ask = st.number_input("FMV PSF", value=1050), st.number_input("Our Ask PSF", value=1100)

# --- CALCULATIONS ---
has_data = all(v is not None and v > 0 for v in [fmv, our_ask, t_high, a_high])
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
    status_text, status_color, diff_pct = "Waiting for Data", "#7f8c8d", 0

# --- DASHBOARD ---
st.title(f"{dev_name}")
c1, c2, c3 = st.columns(3)
c1.metric("Est FMV (PSF)", f"${fmv:,.0f}" if fmv else "-")
c2.metric("Our Asking (PSF)", f"${our_ask:,.0f}" if our_ask else "-")
c3.metric("Variance", f"{diff_pct:+.1%}" if has_data else "-")
st.divider()

# --- PLOTTING ---
if has_data:
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('white')
    
    # Adjust margins: top for header, bottom for PSF labels
    fig.subplots_adjust(top=0.82, bottom=0.18) 

    # 1. Shaded Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # 2. RESTORED & BOLDED PSF RANGE LABELS (At bottom)
    # Using specific Y values to ensure they aren't hidden
    label_y = -1.5
    ax.text(lower_10, label_y, f"-10%\n${lower_10:,.0f} PSF", ha='center', va='top', fontsize=11, weight='bold', color='#7f8c8d')
    ax.text(lower_5, label_y, f"-5%\n${lower_5:,.0f} PSF", ha='center', va='top', fontsize=11, weight='bold', color='#7f8c8d')
    ax.text(upper_5, label_y, f"+5%\n${upper_5:,.0f} PSF", ha='center', va='top', fontsize=11, weight='bold', color='#7f8c8d')
    ax.text(upper_10, label_y, f"+10%\n${upper_10:,.0f} PSF", ha='center', va='top', fontsize=11, weight='bold', color='#7f8c8d')

    # 3. Data Lines
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=10, linewidth=6)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=10, linewidth=6)

    data_min, data_max = min(t_low, a_low, lower_10), max(t_high, a_high, upper_10)
    ax.text(data_min - 60, 2, 'TRANSACTED PSF', weight='bold', ha='right', va='center', fontsize=12)
    ax.text(data_min - 60, 1, 'CURRENT ASKING PSF', weight='bold', ha='right', va='center', fontsize=12)
    ax.text((data_min + data_max)/2, 3.2, f"STATUS: {status_text}", fontsize=28, weight='bold', color=status_color, ha='center')

    # 4. ALIGNED HEADER: LOGO & INFO BAR
    # Logo at top right
    if os.path.exists("logo.png"):
        logo_ax = fig.add_axes([0.80, 0.88, 0.16, 0.08]) 
        logo_ax.imshow(mpimg.imread("logo.png"))
        logo_ax.axis('off')

    # Info Bar: Perfectly aligned with the logo midpoint (y=0.92)
    info_str = (f"Dev: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}\n"
                f"Prepared By: {prepared_by}  |  Date: {today_date}")
    
    ax.text(0.02, 0.92, info_str, transform=fig.transFigure, ha='left', va='center', fontsize=11, fontweight='bold',
            linespacing=1.6, bbox=dict(facecolor='white', edgecolor='#cccccc', boxstyle='round,pad=0.6'))

    # 5. FMV / Our Ask Markers
    ax.scatter(fmv, 2, color='black', s=220, zorder=10)
    ax.text(fmv, 0.3, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=12)
    ax.scatter(our_ask, 1, color=status_color, s=350, edgecolors='black', zorder=11)
    ax.text(our_ask, -0.6, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=14)

    # 6. Final Clean up
    ax.axis('off')
    ax.set_ylim(-2.8, 4.5) # Extra room for the bottom labels
    ax.set_xlim(data_min - 300, data_max + 150)
    st.pyplot(fig)
