import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# CSS for Branding and Alignment
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    
    /* Input Box Styling */
    .stTextInput input, .stNumberInput input {
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        height: 32px !important;
    }

    /* Standardize Metric Alignment */
    [data-testid="stMetric"] {
        text-align: center;
        padding: 15px;
    }

    /* Text Color Rules */
    [data-testid="stMetricLabel"] { color: #000000 !important; font-weight: 800 !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 900 !important; }
    h1, h2, h3, p, span { color: #000000 !important; font-weight: 700 !important; }
    
    section[data-testid="stSidebar"] { background-color: #f8f9fb !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR INPUTS ---
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
file_date_suffix = now.strftime("%Y%m%d")

# --- MAIN DASHBOARD TOP SECTION ---
st.title(f"{dev_name if dev_name else 'Market Analysis'}")

# Row 1: PSF Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Est FMV (PSF)", f"${fmv:,.0f} PSF" if fmv else "-")
m2.metric("Our Asking (PSF)", f"${our_ask:,.0f} PSF" if our_ask else "-")
m3.metric("PSF Variance", f"{diff_pct:+.1%}" if has_data else "-")

# Row 2: Quantum Metrics
q1, q2, q3 = st.columns(3)
q1.metric("Est FMV (Quantum)", f"${(fmv * sqft):,.0f}" if (fmv and valid_sqft) else "-")
q2.metric("Our Asking (Quantum)", f"${(our_ask * sqft):,.0f}" if (our_ask and valid_sqft) else "-")
q3.empty() # Keep alignment consistent

st.divider()

# --- PLOTTING ---
if not has_data:
    st.info("📊 **Graph will be generated once Market Values are entered.**")
else:
    # Use a wider aspect ratio to give labels room
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('white')

    # Shaded Zones
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

    # Vertical Staggered Labels (No Slant)
    y_high, y_low = -0.9, -1.3
    ax.text(lower_10, y_high, f"-10%\n${lower_10:,.0f} PSF", ha='center', fontsize=10, color='#7f8c8d', weight='bold')
    ax.text(lower_5, y_low, f"-5%\n${lower_5:,.0f} PSF", ha='center', fontsize=10, color='#7f8c8d', weight='bold')
    ax.text(upper_5, y_high, f"+5%\n${upper_5:,.0f} PSF", ha='center', fontsize=10, color='#7f8c8d', weight='bold')
    ax.text(upper_10, y_low, f"+10%\n${upper_10:,.0f} PSF", ha='center', fontsize=10, color='#7f8c8d', weight='bold')

    # Lines & Data Points
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=8, linewidth=5)
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=8, linewidth=5)

    # Labels for the lines
    ax.text(t_low, 2.15, f"${int(t_low)} PSF", ha='center', weight='bold')
    ax.text(t_high, 2.15, f"${int(t_high)} PSF", ha='center', weight='bold')
    ax.text(a_low, 0.75, f"${int(a_low)} PSF", ha='center', weight='bold')
    ax.text(a_high, 0.75, f"${int(a_high)} PSF", ha='center', weight='bold')

    # Side labels (Left aligned to the data)
    data_min = min(t_low, a_low, lower_10)
    data_max = max(t_high, a_high, upper_10)
    ax.text(data_min - 30, 2, 'TRANSACTED PSF', weight='bold', ha='right', va='center')
    ax.text(data_min - 30, 1, 'CURRENT ASKING PSF', weight='bold', ha='right', va='center')

    # FMV/Ask Points
    ax.scatter(fmv, 2, color='black', s=150, zorder=5)
    ax.plot([fmv, fmv], [2, 0.4], color='#bdc3c7', linestyle='--', alpha=0.5)
    ax.scatter(our_ask, 1, color=status_color, s=250, edgecolors='black', zorder=6)
    ax.plot([our_ask, our_ask], [1, -0.1], color=status_color, linestyle='--', linewidth=2)

    # --- FLOATING DETAILS BOX (Top Right) ---
    header_info = (
        f"Dev: {dev_name}\n"
        f"Unit: {unit_no}\n"
        f"Size: {sqft} sqft\n"
        f"Type: {u_type}\n"
        f"By: {prepared_by}\n"
        f"Date: {today_date}"
    )
    # Using Axes Coordinates (0 to 1) so it's independent of the data range
    ax.text(0.98, 0.88, header_info, transform=ax.transAxes, ha='right', va='top', 
            fontsize=10, fontweight='bold', linespacing=1.6,
            bbox=dict(facecolor='white', edgecolor='#cccccc', boxstyle='round,pad=0.8'))

    # Logo Alignment
    if os.path.exists("logo.png"):
        logo_img = mpimg.imread("logo.png")
        logo_ax = fig.add_axes([0.84, 0.88, 0.12, 0.08]) 
        logo_ax.imshow(logo_img)
        logo_ax.axis('off')

    # Status & Labels
    ax.text(fmv, 0.2, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=11)
    ax.text(our_ask, -0.4, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=12)
    ax.text((data_min + data_max)/2, 2.7, f"STATUS: {status_text}", fontsize=20, weight='bold', color=status_color, ha='center')

    ax.axis('off')
    ax.set_ylim(-1.8, 3.5)
    ax.set_xlim(data_min - 150, data_max + 150)

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
