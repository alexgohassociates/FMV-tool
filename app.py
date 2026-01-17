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

    /* Input Box Styling (Light Grey with Black Text) */
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
    
    div.stDownloadButton > button:hover {
        background-color: #dddddd !important;
        color: #000000 !important;
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

# --- SIDEBAR: BRANDING & INPUTS ---
with st.sidebar:
    # Top Branding Section
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    st.markdown("### Report Details")
    dev_name = st.text_input("Development", "")
    unit_no  = st.text_input("Unit Number", "")
    sqft     = st.number_input("Size (sqft)", value=0)
    u_type   = st.text_input("Unit Type", "")
    prepared_by = st.text_input("Prepared By", "")
    
    st.markdown("---")
    st.markdown("### Market Range")
    t_low  = st.number_input("Min Transacted", value=0)
    t_high = st.number_input("Max Transacted", value=0)
    a_low  = st.number_input("Min Asking", value=0)
    a_high = st.number_input("Max Asking", value=0)

    st.markdown("---")
    st.markdown("### Pricing Data")
    fmv    = st.number_input("Fair Market Value (PSF)", value=0)
    our_ask = st.number_input("Our Asking (PSF)", value=0)

# --- CALCULATIONS ---
has_data = fmv > 0 and our_ask > 0

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
today_date = now.strftime("%d %b %Y")
file_date = now.strftime("%Y%m%d")

# --- MAIN DASHBOARD ---
st.title(f"{dev_name if dev_name else 'Market Analysis'}")
st.markdown(f"Unit: {unit_no} | Size: {sqft} sqft | Type: {u_type} | Prepared By: {prepared_by} | Date: {today_date}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Est. FMV", f"${fmv:,.0f} PSF")
m2.metric("Our Asking PSF", f"${our_ask:,.0f} PSF")
m3.metric("Price Variance", f"{diff_pct:+.1%}" if has_data else "0%")
m4.metric("Total Asking (Quantum)", f"${(our_ask * sqft):,.0f}")

st.divider()

# --- PLOTTING / PLACEHOLDER ---
if not has_data:
    st.info("📊 **Graph will be generated once Market Values are entered.**")
    # Small preview area
    fig_empty, ax_empty = plt.subplots(figsize=(16, 2))
    ax_empty.axis('off')
    st.pyplot(fig_empty)
else:
    # Full Chart Generation
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('white')

    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # Range Lines
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=8, linewidth=5)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=8, linewidth=5)

    # Text Labels (Black)
    ax.text(t_low, 2.15, f"${int(t_low)} PSF", ha='center', weight='bold', color='black')
    ax.text(t_high, 2.15, f"${int(t_high)} PSF", ha='center', weight='bold', color='black')
    ax.text(a_low, 0.75, f"${int(a_low)} PSF", ha='center', weight='bold', color='black')
    ax.text(a_high, 0.75, f"${int(a_high)} PSF", ha='center', weight='bold', color='black')

    # Data Points
    ax.scatter(fmv, 2, color='black', s=150, zorder=5)
    ax.plot([fmv, fmv], [2, 0.4], color='#bdc3c7', linestyle='--', alpha=0.5)
    ax.scatter(our_ask, 1, color=status_color, s=250, edgecolors='black', zorder=6)
    ax.plot([our_ask, our_ask], [1, -0.1], color=status_color, linestyle='--', linewidth=2)

    # Sidebar alignment
    min_val = min(t_low, a_low, fmv) if any([t_low, a_low, fmv]) else 800
    label_x = min_val - 180 
    ax.text(label_x, 2, 'TRANSACTED PSF', weight='bold', color='black', ha='left', va='center')
    ax.text(label_x, 1, 'CURRENT ASKING PSF', weight='bold', color='black', ha='left', va='center')

    # Info Box & Status
    header_text = f"Dev: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}\nPrepared By: {prepared_by}  |  Date: {today_date}"
    ax.text((t_low + t_high)/2, 3.4, header_text, ha='center', fontsize=12, fontweight='bold', 
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    # Bottom labels adjusted to never overlap
    ax.text(fmv, 0.2, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=11, color='black')
    ax.text(our_ask, -0.4, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color='black', fontsize=12)

    ax.text((t_low + t_high)/2, 2.7, f"STATUS: {status_text}", fontsize=18, weight='bold', color=status_color, ha='center')

    # Chart Logo (Top Right)
    if os.path.exists("logo.png"):
        logo_img = mpimg.imread("logo.png")
        logo_ax = fig.add_axes([0.82, 0.82, 0.15, 0.10]) 
        logo_ax.imshow(logo_img)
        logo_ax.axis('off')

    ax.axis('off')
    ax.set_ylim(-0.8, 3.8) 
    ax.set_xlim(label_x - 20, max(t_high, a_high, fmv) + 120)

    st.pyplot(fig)

    # --- SIDEBAR DOWNLOAD ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Download")
    fn_dev = dev_name.replace(" ", "_") if dev_name else "Project"
    fn_unit = unit_no.replace("-", "_").replace(" ", "_") if unit_no else "Unit"
    fn_name = prepared_by.replace(" ", "_") if prepared_by else "User"
    custom_filename = f"{fn_dev}_{fn_unit}_{file_date}_{fn_name}.pdf"

    buf_pdf = io.BytesIO()
    fig.savefig(buf_pdf, format="pdf", bbox_inches='tight')
    st.sidebar.download_button(label="Download PDF Report", data=buf_pdf.getvalue(), file_name=custom_filename, mime="application/pdf")
