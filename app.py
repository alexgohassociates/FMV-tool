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

# --- CSS: V2.3 (SAFE & HIGH CONTRAST) ---
st.markdown("""
    <style>
    /* 1. Main App Background -> White */
    .stApp { background-color: white !important; }
    
    /* 2. Global Text -> Black */
    h1, h2, h3, p, div, label, .stMetric label, [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* 3. Sidebar -> White */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }

    /* 4. Inputs -> Light Grey */
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stNumberInput input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        border-color: #d1d5db !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        margin-bottom: 2px !important;
    }

    div.stDownloadButton > button {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        width: 100%;
    }

    /* 5. Header Cleanup */
    /* Hide Decoration & Toolbar */
    [data-testid="stDecoration"], [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Force Header Background to White */
    [data-testid="stHeader"] {
        background-color: white !important;
        border-bottom: 1px solid #e0e0e0;
    }

    /* 6. SIDEBAR BUTTON FIX (The "White on White" Killer) */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #000000 !important;
        background-color: white !important;
        z-index: 100 !important;
        
        /* Add a border so you can see the box even if the icon is invisible */
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-top: 5px;
        margin-left: 5px;
    }
    
    /* Force the actual SVG Arrow to be Black */
    [data-testid="stSidebarCollapsedControl"] svg, 
    [data-testid="stSidebarCollapsedControl"] i {
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
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
    
    st.markdown("---")
    st.markdown("### Valuation & Price")
    
    c_fmv1, c_fmv2 = st.columns(2)
    with c_fmv1:
        st.number_input("FMV (PSF)", value=None, step=10.0, key="fmv_psf", on_change=calc_fmv_quantum)
    with c_fmv2:
        st.number_input("FMV (Quantum)", value=None, step=1000.0, key="fmv_quantum", on_change=calc_fmv_psf)

    c_ask1, c_ask2 = st.columns(2)
    with c_ask1:
        st.number_input("Ask (PSF)", value=None, step=10.0, key="ask_psf", on_change=calc_ask_quantum)
    with c_ask2:
        st.number_input("Ask (Quantum)", value=None, step=1000.0, key="ask_quantum", on_change=calc_ask_psf)

# --- CALCULATIONS ---
fmv_val = st.session_state.fmv_psf
ask_val = st.session_state.ask_psf

required_values = [sqft, fmv_val, ask_val, t1, t2, a1, a2]
has_data = all(v is not None and v > 0 for v in required_values)

tz_sg = timezone(timedelta(hours=8))
today_date = datetime.now(tz_sg).strftime("%d %b %Y")

if has_data:
    sqft = float(sqft)
    fmv = float(fmv_val)
    our_ask = float(ask_val)
    
    upper_5 = fmv * 1.05
    upper_10 = fmv * 1.10
    
    upper_5_quant = upper_5 * sqft
    upper_10_quant = upper_10 * sqft
    
    diff_pct = (our_ask - fmv) / fmv
    
    fmv_quant = fmv * sqft
    ask_quant = our_ask * sqft
    
    if diff_pct <= 0.05:
        status_text = "Asking ≤ +5% of FMV"
        status_color = "#2ecc71" # Green
    elif diff_pct <= 0.10:
        status_text = "Asking +5% to +10% of FMV"
        status_color = "#f1c40f" # Yellow
    else:
        status_text = "Asking > +10% of FMV"
        status_color = "#e74c3c" # Red
else:
    status_text = "Waiting for Data..."
    status_color = "#bdc3c7"
    diff_pct = 0
    fmv_quant, ask_quant = 0, 0
    fmv, our_ask = 0, 0
    upper_5, upper_10 = 0, 0
    upper_5_quant, upper_10_quant = 0, 0

# --- DASHBOARD LAYOUT ---
display_dev_name = dev_name if dev_name else "Development Name"
display_unit_no = unit_no if unit_no else "-"
display_sqft = f"{int(sqft):,}" if (sqft and sqft > 0) else "-"
display_u_type = u_type if u_type else "-"

st.title(f"{display_dev_name}")
st.caption(f"Unit: {display_unit_no} | Size: {display_sqft} sqft | Type: {display_u_type}")

c1, c2, c3 = st.columns(3)
c1.metric("FMV (PSF)", f"${fmv:,.0f} psf" if has_data else "-")
c2.metric("Asking (PSF)", f"${our_ask:,.0f} psf" if has_data else "-")
if has_data:
    c3.metric("Variance", f"{diff_pct:+.1%}", delta_color="inverse")
else:
    c3.metric("Variance", "-")

c4, c5, c6 = st.columns(3) 
c4.metric("FMV (Quantum)", f"${fmv_quant:,.0f}" if has_data else "-")
c5.metric("Asking (Quantum)", f"${ask_quant:,.0f}" if has_data else "-")

st.divider()

# --- PLOTTING ENGINE ---
fig = None

if has_data:
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    fig.patch.set_facecolor('white')
    
    all_values = [t_low, t_high, a_low, a_high, fmv, our_ask, upper_10]
    data_min = min(all_values)
    data_max = max(all_values)
    data_range = data_max - data_min
    padding = data_range * 0.25 
    
    y_min_limit = -9.0 
    y_max_limit = 5.5
    x_min_limit = data_min - padding
    x_max_limit = data_max + (padding*0.5)

    y_shade = [y_min_limit, -0.5] 
    
    ax.fill_betweenx(y_shade, x_min_limit, upper_5, color='#2ecc71', alpha=0.15)
    ax.fill_betweenx(y_shade, upper_5, upper_10, color='#f1c40f', alpha=0.15)
    ax.fill_betweenx(y_shade, upper_10, x_max_limit, color='#e74c3c', alpha=0.15)

    y_labels_5 = -5.0 
    y_labels_10 = -7.0 
    style_dict = dict(ha='center', va='top', fontsize=10, weight='bold', color='#95a5a6')
    
    ax.text(upper_5, y_labels_5, f"+5%\n${upper_5:,.0f} PSF\n(${upper_5_quant:,.0f})", **style_dict)
    ax.text(upper_10, y_labels_10, f"+10%\n${upper_10:,.0f} PSF\n(${upper_10_quant:,.0f})", **style_dict)

    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=7, linewidth=5, solid_capstyle='round')
    ax.text(t_low, 2.45, f"${t_low:,.0f} PSF", ha='center', va='bottom', fontsize=10, weight='bold', color='#3498db')
    ax.text(t_high, 2.45, f"${t_high:,.0f} PSF", ha='center', va='bottom', fontsize=10, weight='bold', color='#3498db')

    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=7, linewidth=5, solid_capstyle='round')
    ax.text(a_low, 0.55, f"${a_low:,.0f} PSF", ha='center', va='top', fontsize=10, weight='bold', color='#34495e')
    ax.text(a_high, 0.55, f"${a_high:,.0f} PSF", ha='center', va='top', fontsize=10, weight='bold', color='#34495e')

    text_x_pos = data_min - (data_range * 0.05) 
    ax.text(text_x_pos, 2, 'RECENT TRANSACTED', weight='bold', ha='right', va='center', fontsize=12, color='#3498db')
    ax.text(text_x_pos, 1, 'CURRENT ASKING', weight='bold', ha='right', va='center', fontsize=12, color='#34495e')

    ax.vlines(fmv, 2, -1.3, linestyles='dotted', colors='black', linewidth=2, zorder=5)
    ax.scatter(fmv, 2, color='black', s=100, zorder=10, marker='D')
    ax.text(fmv, -1.5, f"FMV\n${fmv:,.0f} PSF\n(${fmv_quant:,.0f})", 
            ha="center", va="top", weight="bold", fontsize=11, color='black')

    ax.vlines(our_ask, 1, -2.8, linestyles='dotted', colors=status_color, linewidth=2, zorder=5)
    ax.scatter(our_ask, 1, color=status_color, s=180, edgecolors='black', zorder=11, linewidth=2)
    ax.text(our_ask, -3.0, f"ASKING\n${our_ask:,.0f} PSF\n(${ask_quant:,.0f})", 
            ha="center", va="top", weight="bold", fontsize=11, color='black')

    if os.path.exists("logo.png"):
        try:
            logo_img = Image.open("logo.png")
            logo_ax = fig.add_axes([0.75, 0.85, 0.15, 0.12]) 
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')
        except:
            pass 

    safe_prepared_by = prepared_by if prepared_by else "-"
    info_str = (f"{display_dev_name} ({display_unit_no}) | {display_sqft} sqft | {display_u_type}\n"
                f"Analysis by {safe_prepared_by} | {today_date}")
    ax.text(0.03, 0.91, info_str, transform=fig.transFigure, ha='left', va='center', fontsize=10, fontweight='bold',
            color='#555555', bbox=dict(facecolor='#f8f9fa', edgecolor='none', boxstyle='round,pad=0.5'))

    ax.scatter([0.04], [0.82], s=180, color=status_color, marker='o', transform=fig.transFigure, clip_on=False, zorder=20)
    ax.text(0.055, 0.82, f"STATUS: {status_text}", transform=fig.transFigure, ha='left', va='center',
            fontsize=12, weight='bold', color='#555555')

    ax.axis('off')
    ax.set_ylim(y_min_limit, y_max_limit) 
    ax.set_xlim(x_min_limit, x_max_limit)
    
    st.pyplot(fig)
elif not has_data:
    st.info("👈 Please enter property details and market data in the sidebar to generate the analysis.")

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
