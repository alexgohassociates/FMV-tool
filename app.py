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
        margin-bottom: 2px !important;
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
    [data-testid="stSidebar"] .stElementContainer {
        margin-bottom: 0.8rem !important;
    }
    [data-testid="stSidebar"] h3 {
        padding-top: 0.5rem !important;
        padding-bottom: 0.2rem !important;
        margin-bottom: 0 !important;
    }
    [data-testid="stSidebar"] hr {
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR INPUTS (BLANK DEFAULTS) ---
with st.sidebar:
    # 1. Branding (Logo on Sidebar Top)
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    # 2. Property Details
    st.markdown("### Property Details")
    dev_name = st.text_input("Development / Address", "")
    unit_no  = st.text_input("Unit", "")
    sqft     = st.number_input("Size (sqft)", value=None, step=1)
    u_type   = st.text_input("Type", "")
    prepared_by = st.text_input("Agent Name", "")
    
    st.markdown("---")
    
    # 3. Market Data
    st.markdown("### Market Data")
    t1 = st.number_input("Lowest Transacted (PSF)", value=None, step=10)
    t2 = st.number_input("Highest Transacted (PSF)", value=None, step=10)
    
    if t1 is not None and t2 is not None:
        t_low, t_high = min(t1, t2), max(t1, t2)
    else:
        t_low, t_high = 0, 0
    
    a1 = st.number_input("Lowest Asking (PSF)", value=None, step=10)
    a2 = st.number_input("Highest Asking (PSF)", value=None, step=10)
    
    if a1 is not None and a2 is not None:
        a_low, a_high = min(a1, a2), max(a1, a2)
    else:
        a_low, a_high = 0, 0
    
    st.markdown("### Valuation")
    fmv = st.number_input("FMV (PSF)", value=None, step=10)
    our_ask = st.number_input("Asking Price (PSF)", value=None, step=10)

# --- CALCULATIONS & DATA VALIDATION ---
required_values = [sqft, fmv, our_ask, t1, t2, a1, a2]
has_data = all(v is not None and v > 0 for v in required_values)

tz_sg = timezone(timedelta(hours=8))
today_date = datetime.now(tz_sg).strftime("%d %b %Y")

if has_data:
    sqft = float(sqft)
    fmv = float(fmv)
    our_ask = float(our_ask)
    
    # Calculate thresholds for chart logic
    upper_5 = fmv * 1.05
    upper_10 = fmv * 1.10
    
    # For chart labels
    lower_5 = fmv * 0.95
    lower_10 = fmv * 0.90
    
    diff_pct = (our_ask - fmv) / fmv
    
    # Quantum Calculations
    fmv_quantum = fmv * sqft
    ask_quantum = our_ask * sqft
    
    # --- UPDATED STATUS LOGIC ---
    if diff_pct <= 0.05:
        # Green Zone: Less than or equal to +5% (Includes negatives)
        status_text = "Asking ≤ +5% of FMV"
        status_color = "#2ecc71" # Green
    elif diff_pct <= 0.10:
        # Yellow Zone: Between 5% and 10%
        status_text = "Asking +5% to +10% of FMV"
        status_color = "#f1c40f" # Yellow
    else:
        # Red Zone: Greater than 10%
        status_text = "Asking > +10% of FMV"
        status_color = "#e74c3c" # Red
else:
    status_text = "Waiting for Data..."
    status_color = "#bdc3c7" # Grey
    diff_pct = 0
    fmv_quantum, ask_quantum = 0, 0
    fmv, our_ask = 0, 0

# --- DASHBOARD LAYOUT ---
display_dev_name = dev_name if dev_name else "Development Name"
display_unit_no = unit_no if unit_no else "-"
display_sqft = f"{int(sqft):,}" if (sqft and sqft > 0) else "-"
display_u_type = u_type if u_type else "-"

st.title(f"{display_dev_name}")
st.caption(f"Unit: {display_unit_no} | Size: {display_sqft} sqft | Type: {display_u_type}")

# Row 1: PSF Metrics & Variance
c1, c2, c3 = st.columns(3)
c1.metric("FMV (PSF)", f"${fmv:,.0f} psf" if has_data else "-")
c2.metric("Asking (PSF)", f"${our_ask:,.0f} psf" if has_data else "-")
if has_data:
    c3.metric("Variance", f"{diff_pct:+.1%}", delta_color="inverse")
else:
    c3.metric("Variance", "-")

# Row 2: Quantum Metrics
c4, c5, c6 = st.columns(3) 
c4.metric("FMV (Quantum)", f"${fmv_quantum:,.0f}" if has_data else "-")
c5.metric("Asking (Quantum)", f"${ask_quantum:,.0f}" if has_data else "-")

st.divider()

# --- PLOTTING ENGINE ---
fig = None

if has_data:
    # Create Figure
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    fig.patch.set_facecolor('white')
    
    # Dynamic limits
    all_values = [t_low, t_high, a_low, a_high, fmv, our_ask, lower_10, upper_10]
    data_min = min(all_values)
    data_max = max(all_values)
    data_range = data_max - data_min
    padding = data_range * 0.25 
    
    # Limits for plotting
    y_min_limit = -8.0
    y_max_limit = 5.5
    x_min_limit = data_min - padding
    x_max_limit = data_max + (padding*0.5)

    # 1. Shaded Zones - 3 ZONES LOGIC
    # Restricted height (bottom half only)
    y_shade = [y_min_limit, -0.5] 
    
    # A) Green Zone: From far left to +5%
    ax.fill_betweenx(y_shade, x_min_limit, upper_5, color='#2ecc71', alpha=0.15)
    
    # B) Yellow Zone: From +5% to +10%
    ax.fill_betweenx(y_shade, upper_5, upper_10, color='#f1c40f', alpha=0.15)
    
    # C) Red Zone: From +10% to far right
    ax.fill_betweenx(y_shade, upper_10, x_max_limit, color='#e74c3c', alpha=0.15)

    # 2. Zone Labels
    # We maintain the 5% and 10% markers for reference
    y_labels_5 = -5.0 
    y_labels_10 = -6.5
    style_dict = dict(ha='center', va='top', fontsize=10, weight='bold', color='#95a5a6')
    
    ax.text(lower_5, y_labels_5, f"-5%\n${lower_5:,.0f} PSF", **style_dict)
    ax.text(upper_5, y_labels_5, f"+5%\n${upper_5:,.0f} PSF", **style_dict)
    
    ax.text(lower_10, y_labels_10, f"-10%\n${lower_10:,.0f} PSF", **style_dict)
    ax.text(upper_10, y_labels_10, f"+10%\n${upper_10:,.0f} PSF", **style_dict)

    # 3. Market Range Lines (Dumbbell Plot)
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=7, linewidth=5, solid_capstyle='round')
    ax.text(t_low, 2.45, f"${t_low:,.0f} PSF", ha='center', va='bottom', fontsize=10, weight='bold', color='#3498db')
    ax.text(t_high, 2.45, f"${t_high:,.0f} PSF", ha='center', va='bottom', fontsize=10, weight='bold', color='#3498db')

    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=7, linewidth=5, solid_capstyle='round')
    ax.text(a_low, 0.55, f"${a_low:,.0f} PSF", ha='center', va='top', fontsize=10, weight='bold', color='#34495e')
    ax.text(a_high, 0.55, f"${a_high:,.0f} PSF", ha='center', va='top', fontsize=10, weight='bold', color='#34495e')

    # 4. Labels for Lines
    text_x_pos = data_min - (data_range * 0.05) 
    ax.text(text_x_pos, 2, 'RECENT TRANSACTED', weight='bold', ha='right', va='center', fontsize=12, color='#3498db')
    ax.text(text_x_pos, 1, 'CURRENT ASKING', weight='bold', ha='right', va='center', fontsize=12, color='#34495e')

    # 5. FMV vs Ask Markers
    # FMV Marker
    ax.vlines(fmv, 2, -1.3, linestyles='dotted', colors='black', linewidth=2, zorder=5)
    ax.scatter(fmv, 2, color='black', s=100, zorder=10, marker='D')
    ax.text(fmv, -1.5, f"FMV\n${fmv:,.0f} PSF", ha="center", va="top", weight="bold", fontsize=11, color='black')

    # ASKING Marker
    # Drop line and Circle use status_color (Green/Yellow/Red)
    # Text uses 'black' for readability
    ax.vlines(our_ask, 1, -2.8, linestyles='dotted', colors=status_color, linewidth=2, zorder=5)
    ax.scatter(our_ask, 1, color=status_color, s=180, edgecolors='black', zorder=11, linewidth=2)
    ax.text(our_ask, -3.0, f"ASKING\n${our_ask:,.0f} PSF", ha="center", va="top", weight="bold", fontsize=11, color='black')

    # 6. HEADERS & LOGO (Top Layer)
    if os.path.exists("logo.png"):
        try:
            logo_img = Image.open("logo.png")
            logo_ax = fig.add_axes([0.75, 0.85, 0.15, 0.12]) 
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')
        except:
            pass 

    # Footer/Details Info
    safe_prepared_by = prepared_by if prepared_by else "-"
    info_str = (f"{display_dev_name} ({display_unit_no}) | {display_sqft} sqft | {display_u_type}\n"
                f"Analysis by {safe_prepared_by} | {today_date}")
    ax.text(0.03, 0.91, info_str, transform=fig.transFigure, ha='left', va='center', fontsize=10, fontweight='bold',
            color='#555555', bbox=dict(facecolor='#f8f9fa', edgecolor='none', boxstyle='round,pad=0.5'))

    # Status Banner
    ax.scatter([0.04], [0.82], s=180, color=status_color, marker='o', transform=fig.transFigure, clip_on=False, zorder=20)
    ax.text(0.055, 0.82, f"STATUS: {status_text}", transform=fig.transFigure, ha='left', va='center',
            fontsize=12, weight='bold', color='#555555')

    # Final visual tweaks
    ax.axis('off')
    ax.set_ylim(y_min_limit, y_max_limit) 
    ax.set_xlim(x_min_limit, x_max_limit)
    
    st.pyplot(fig)
elif not has_data:
    st.info("👈 Please enter property details and market data in the sidebar to generate the analysis.")

# --- SIDEBAR DOWNLOAD BUTTON (PDF FORMAT) ---
with st.sidebar:
    st.markdown("---")
    if fig is not None:
        filename_date = datetime.now(tz_sg).strftime("%d-%m-%Y")
        safe_dev = (dev_name if dev_name else "Property").replace("/", "-").replace("\\", "-")
        safe_unit = (unit_no if unit_no else "Unit").replace("/", "-")
        safe_sqft = str(int(sqft)) if (sqft and sqft > 0) else "0"
        safe_agent = prepared_by if prepared_by else "Agent"
        
        final_filename = f"{safe_dev}-{safe_unit}-{safe_sqft}-{filename_date}-{safe_agent}.pdf"

        pdf_buffer = io.BytesIO()
        fig.savefig(pdf_buffer, format='pdf', bbox_inches='tight', dpi=300)
        
        st.download_button(
            label="📥 Download Analysis as PDF",
            data=pdf_buffer,
            file_name=final_filename,
            mime="application/pdf",
            use_container_width=True
        )
