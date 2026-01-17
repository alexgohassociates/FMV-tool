import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# CSS for Compact Sidebar, Grey Input Boxes, and Matching Grey Download Button
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    
    /* COMPACT SIDEBAR CODE */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    
    div[data-testid="stTextSelectionContainer"] > div {
        margin-bottom: -15px !important;
    }

    /* Input Box Styling */
    .stTextInput input, .stNumberInput input {
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        height: 32px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }

    /* MATCHING DOWNLOAD BUTTON STYLING */
    div.stDownloadButton > button {
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        font-weight: 800 !important;
        width: 100% !important;
        border-radius: 5px !important;
        transition: 0.3s;
    }
    
    div.stDownloadButton > button:hover {
        background-color: #dddddd !important;
        border-color: #999999 !important;
        color: #000000 !important;
    }

    /* Text and Labels Styling */
    [data-testid="stMetricLabel"] { color: #000000 !important; font-weight: 800 !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #1f77b4 !important; font-weight: 900 !important; }
    h1, h2, h3, p, span { color: #000000 !important; font-weight: 700 !important; }
    
    section[data-testid="stSidebar"] { background-color: #f8f9fb !important; }
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label { 
        color: #000000 !important; 
        font-weight: 800 !important;
        font-size: 0.85rem !important;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: COMPACT CONTROLS ---
with st.sidebar:
    st.markdown("### Report Details")
    dev_name = st.text_input("Development", "KRHR")
    unit_no  = st.text_input("Unit Number", "02-57")
    sqft     = st.number_input("Size (sqft)", value=1079)
    u_type   = st.text_input("Unit Type", "3 Room")
    prepared_by = st.text_input("Prepared By", "Alex Goh")
    
    st.markdown("---")
    st.markdown("### Market Range")
    t_low  = st.number_input("Min Transacted", value=1000)
    t_high = st.number_input("Max Transacted", value=1200)
    a_low  = st.number_input("Min Asking", value=1050)
    a_high = st.number_input("Max Asking", value=1300)

    st.markdown("---")
    st.markdown("### Pricing Data")
    fmv    = st.number_input("Fair Market Value (PSF)", value=1150)
    our_ask = st.number_input("Our Asking (PSF)", value=1250)
    
# --- CALCULATIONS ---
lower_5, upper_5 = fmv * 0.95, fmv * 1.05
lower_10, upper_10 = fmv * 0.90, fmv * 1.10
diff_pct = (our_ask - fmv) / fmv

if abs(diff_pct) <= 0.05:
    status_text, status_color = "WITHIN 5% OF FMV", "#2ecc71"
elif abs(diff_pct) <= 0.10:
    status_text, status_color = "BETWEEN 5-10% OF FMV", "#f1c40f"
else:
    status_text, status_color = "MORE THAN 10% OF FMV", "#e74c3c"

tz_sg = timezone(timedelta(hours=8))
now = datetime.now(tz_sg)
today_date = now.strftime("%d %b %Y")
file_date = now.strftime("%Y%m%d")

# --- MAIN DASHBOARD ---
st.title(f"{dev_name} | Market Analysis")
st.markdown(f"Unit: {unit_no} | Size: {sqft} sqft | Type: {u_type} | Prepared By: {prepared_by} | Date: {today_date}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Est. FMV", f"${fmv:,.0f} PSF")
m2.metric("Our Asking PSF", f"${our_ask:,.0f} PSF")
m3.metric("Price Variance", f"{diff_pct:+.1%}")
m4.metric("Total Asking (Quantum)", f"${(our_ask * sqft):,.0f}")

st.divider()

# --- PLOTTING LOGIC ---
fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
fig.patch.set_facecolor('white')

ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=8, linewidth=5)
ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=8, linewidth=5)

ax.text(t_low, 2.15, f"${int(t_low)} PSF", ha='center', weight='bold', color='#1f77b4')
ax.text(t_high, 2.15, f"${int(t_high)} PSF", ha='center', weight='bold', color='#1f77b4')
ax.text(a_low, 0.75, f"${int(a_low)} PSF", ha='center', weight='bold', color='#34495e')
ax.text(a_high, 0.75, f"${int(a_high)} PSF", ha='center', weight='bold', color='#34495e')

ax.scatter(fmv, 2, color='black', s=150, zorder=5)
ax.plot([fmv, fmv], [2, 0.4], color='#bdc3c7', linestyle='--', alpha=0.5)
ax.scatter(our_ask, 1, color=status_color, s=250, edgecolors='black', zorder=6)
ax.plot([our_ask, our_ask], [1, 0.4], color=status_color, linestyle='--', linewidth=2)

min_plot_x = min(t_low, a_low, fmv, lower_10)
label_x = min_plot_x - 180 
ax.text(label_x, 2, 'TRANSACTED PSF', weight='bold', color='#2980b9', ha='left', va='center')
ax.text(label_x, 1, 'CURRENT ASKING PSF', weight='bold', color='#2c3e50', ha='left', va='center')

header_text = f"Dev: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}\nPrepared By: {prepared_by}  |  Date: {today_date}"
ax.text((t_low + t_high)/2, 3.4, header_text, ha='center', fontsize=12, fontweight='bold', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

ax.text(fmv, 0.2, f"FMV\n${fmv:,.0f} PSF", ha="center", weight="bold", fontsize=11)
ax.text(our_ask, 0.2, f"OUR ASK\n${our_ask:,.0f} PSF", ha="center", weight="bold", color=status_color, fontsize=12)

ax.text((t_low + t_high)/2, 2.7, f"STATUS: {status_text}", fontsize=18, weight='bold', color=status_color, ha='center')

if os.path.exists("logo.png"):
    logo_img = mpimg.imread("logo.png")
    logo_ax = fig.add_axes([0.82, 0.82, 0.15, 0.10]) 
    logo_ax.imshow(logo_img)
    logo_ax.axis('off')

ax.axis('off')
ax.set_ylim(-0.6, 3.8) 
ax.set_xlim(label_x - 20, max(t_high, a_high, fmv, upper_10) + 120)

st.pyplot(fig)

# --- DOWNLOAD SECTION ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Download")

fn_dev = dev_name.replace(" ", "_")
fn_unit = unit_no.replace("-", "_").replace(" ", "_")
fn_name = prepared_by.replace(" ", "_")
custom_filename = f"{fn_dev}_{fn_unit}_{file_date}_{fn_name}.pdf"

buf_pdf = io.BytesIO()
fig.savefig(buf_pdf, format="pdf", bbox_inches='tight')
st.sidebar.download_button(
    label="Download PDF Report", 
    data=buf_pdf.getvalue(), 
    file_name=custom_filename, 
    mime="application/pdf"
)
