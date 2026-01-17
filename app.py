import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# CSS for Branding and Layout
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    
    /* COMPACT SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div[data-testid="stTextSelectionContainer"] > div { margin-bottom: -15px !important; }

    /* Input Box Styling */
    .stTextInput input, .stNumberInput input {
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        height: 32px !important;
    }

    /* Button Styling */
    div.stDownloadButton > button {
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        font-weight: 800 !important;
        width: 100% !important;
        border-radius: 5px !important;
    }

    /* Text Color Rules */
    [data-testid="stMetricLabel"] { color: #000000 !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #1f77b4 !important; font-weight: 900 !important; }
    h1, h2, h3, p, span { color: #000000 !important; font-weight: 700 !important; }
    
    section[data-testid="stSidebar"] { background-color: #f8f9fb !important; }
    section[data-testid="stSidebar"] label { 
        color: #000000 !important; 
        font-weight: 800 !important;
        font-size: 0.85rem !important;
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

    if abs(diff_pct) <= 0.05:
        status_text, status_color = "WITHIN 5% OF FMV", "#2ecc71"
    elif abs(diff_pct) <= 0.10:
        status_text, status_color = "BETWEEN 5-10% OF FMV", "#f1c40f"
    else:
        status_text, status_color = "MORE THAN 10% OF FMV", "#e74c3c"
else:
    status_text, status_color = "Awaiting Input", "#7f8c8d"
    diff_pct = 0

tz_sg = timezone(timedelta(hours=8))
now = datetime.now(tz_sg)
today_date = now.strftime("%d/%m/%Y")
file_date_suffix = now.strftime("%d_%m_%Y")

# --- MAIN DASHBOARD ---
st.title(f"{dev_name if dev_name else 'Market Analysis'}")
st.markdown(f"Unit: {unit_no if unit_no else '-'} | Size: {sqft if sqft else '-'} sqft | Type: {u_type if u_type else '-'} | Prepared By: {prepared_by if prepared_by else '-'} | Date: {today_date}")

# Metrics
r1_c1, r1_c2, r1_c3 = st.columns(3)
r1_c1.metric("Est FMV (PSF)", f"${fmv:,.0f} PSF" if fmv else "-")
r1_c2.metric("Our Asking (PSF)", f"${our_ask:,.0f} PSF" if our_ask else "-")
r1_c3.metric("Variance", f"{diff_pct:+.1%}" if has_data else "-")

r2_c1, r2_c2, r2_c3 = st.columns(3)
r2_c1.metric("Est FMV (Quantum)", f"${(fmv * sqft):,.0f}" if (fmv and valid_sqft) else "-")
r2_c2.metric("Our Asking (Quantum)", f"${(our_ask * sqft):,.0f}" if (our_ask and valid_sqft) else "-")

st.divider()

# --- PLOTTING ---
if not has_data:
    st.info("📊 **Graph will be generated once all values are entered.**")
    fig_empty, ax_empty = plt.subplots(figsize=(16, 2))
    ax_empty.axis('off')
    st.pyplot(fig_empty)
else:
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('white')

    # Shaded Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # Zone Range Labels (THE MISSING PSF RANGES)
    ax.text(lower_10, -0.6, f"-$10%\n${lower_10:,.0f}", ha='center', fontsize=9, color='#7f8c8d')
    ax.text(lower_5, -0.6, f"-$5%\n${lower_5:,.0f}", ha='center', fontsize=9, color='#7f8c8d')
    ax.text(upper_5, -0.6, f"+$5%\n${upper_5:,.0f}", ha='center', fontsize=9, color='#7f8c8d')
    ax.text(upper_10, -0.6, f"+$10%\n${upper_10:,.0f}", ha='center', fontsize=9, color='#7f8c8d')

    # Data Lines
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=8, linewidth=5)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=8, linewidth=5)

    ax.text(t_low, 2.15, f"${int(t_low)} PSF", ha='center', weight='bold')
    ax.text(t_high, 2.15, f"${int(t_high)} PSF", ha='center', weight='bold')
    ax.text(a_low, 0.75, f"${int(a_low)} PSF", ha='center', weight='bold')
    ax.text(a_high, 0.75, f"${int(a_high)} PSF", ha='center', weight='bold')

    # Markers
    ax.scatter(fmv, 2, color='black', s=150, zorder=5)
    ax.plot([fmv, fmv], [2, 0.4], color='#bdc3c7', linestyle='--', alpha=0.5)
    ax.scatter(our_ask, 1, color=status_color, s=250, edgecolors='black', zorder=6)
    ax.plot([our_ask, our_ask], [1, -0.1], color=status_color, linestyle='--', linewidth=2)

    label_x = min(t_low, a_low, fmv, lower_10) - 150 
    ax.text(label_x, 2, 'TRANSACTED PSF', weight='bold', ha='left', va='center')
    ax.text(label_x, 1, 'CURRENT ASKING PSF', weight='bold', ha='left', va='center')

    # Header and Status
    header_text = f"Dev/Address: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}\nPrepared By: {prepared_by}  |  Date: {today_date}"
    ax.text((t_low + t_high)/2, 3.4, header_text, ha='center', fontsize=12, fontweight='bold', 
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    ax.text(fmv, 0.2, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=11)
    ax.text(our_ask, -0.4, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=12)
    ax.text((t_low + t_high)/2, 2.7, f"STATUS: {status_text}", fontsize=18, weight='bold', color=status_color, ha='center')

    if os.path.exists("logo.png"):
        logo_img = mpimg.imread("logo.png")
        logo_ax = fig.add_axes([0.82, 0.82, 0.15, 0.10]) 
        logo_ax.imshow(logo_img)
        logo_ax.axis('off')

    ax.axis('off')
    ax.set_ylim(-1.0, 3.8) 
    ax.set_xlim(label_x - 20, max(t_high, a_high, fmv, upper_10) + 120)

    st.pyplot(fig)

    # --- DOWNLOAD ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Download")
    fn_dev = dev_name.replace(" ", "_") if dev_name else "Project"
    fn_unit = unit_no.replace("-", "_").replace(" ", "_") if unit_no else "Unit"
    fn_name = prepared_by.replace(" ", "_") if prepared_by else "User"
    custom_filename = f"{fn_dev}_{fn_unit}_{file_date_suffix}_{fn_name}.pdf"

    buf_pdf = io.BytesIO()
    fig.savefig(buf_pdf, format="pdf", bbox_inches='tight')
    st.sidebar.download_button(label="Download PDF Report", data=buf_pdf.getvalue(), file_name=custom_filename, mime="application/pdf")
