import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import os
from datetime import datetime, timedelta, timezone

# 1. Page Configuration
st.set_page_config(
    page_title="ProProperty PSF Analyzer", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for White Background and Bold Black Site Headers
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    /* Metric Labels and Values - Bold Black */
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #1f77b4 !important;
        font-weight: 900 !important;
    }
    /* Main Titles - Bold Black */
    h1, h2, h3 {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    /* Meta text */
    .stMarkdown p, .stCaption {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8f9fb !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.title("📄 Report Details")
    dev_name = st.text_input("Development", "KRHR")
    unit_no  = st.text_input("Unit Number", "02-57")
    sqft     = st.number_input("Size (sqft)", value=1079)
    u_type   = st.text_input("Unit Type", "3 Room")
    
    st.divider()
    st.title("💰 Pricing Data")
    fmv    = st.number_input("Fair Market Value (PSF)", value=1150)
    our_ask = st.number_input("Our Asking (PSF)", value=1250)
    
    st.divider()
    st.title("📊 Market Range")
    t_low  = st.number_input("Min Transacted PSF", value=1000)
    t_high = st.number_input("Max Transacted PSF", value=1200)
    a_low  = st.number_input("Min Asking PSF", value=1050)
    a_high = st.number_input("Max Asking PSF", value=1300)

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
gen_time = datetime.now(tz_sg).strftime("%d %b %Y, %H:%M (GMT+8)")

# --- MAIN DASHBOARD ---
st.title(f"🏢 {dev_name} | Market Analysis")
st.markdown(f"Unit: **{unit_no}** | Size: **{sqft} sqft** | Type: **{u_type}** | Data as of: **{gen_time}**")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Our Asking PSF", f"${our_ask:,.0f} PSF")
m2.metric("Est. FMV", f"${fmv:,.0f} PSF")
m3.metric("Price Variance", f"{diff_pct:+.1%}")
m4.metric("Total Asking", f"${(our_ask * sqft):,.0f}")

st.divider()

# --- PLOTTING LOGIC ---
fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor('white')

# Zones
ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.12)
ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)
ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)

# Range Lines
ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', linewidth=6)
ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', linewidth=6)

# PSF Labels
ax.text(t_low, 2.15, f"${int(t_low)} PSF", ha='center', weight='bold', color='#1f77b4')
ax.text(t_high, 2.15, f"${int(t_high)} PSF", ha='center', weight='bold', color='#1f77b4')
ax.text(a_low, 0.75, f"${int(a_low)} PSF", ha='center', weight='bold', color='#34495e')
ax.text(a_high, 0.75, f"${int(a_high)} PSF", ha='center', weight='bold', color='#34495e')

# Indicators
ax.scatter(fmv, 2, color='black', s=180, zorder=5)
ax.plot([fmv, fmv], [2, 0.4], color='#bdc3c7', linestyle='--', alpha=0.5)
ax.scatter(our_ask, 1, color=status_color, s=300, edgecolors='black', zorder=6)
ax.plot([our_ask, our_ask], [1, 0.4], color=status_color, linestyle='--', linewidth=2.5)

# Boundaries
boundary_y = -0.3
for val, lbl in zip([lower_10, lower_5, upper_5, upper_10], ["-10%", "-5%", "+5%", "+10%"]):
    ax.text(val, boundary_y, f"{lbl}\n${int(val)} PSF", ha='center', fontsize=9, color='grey')

# Axis Titles
min_plot_x = min(t_low, a_low, fmv, lower_10)
label_x = min_plot_x - 180 
ax.text(label_x, 2, 'TRANSACTED PSF', weight='bold', color='#2980b9', ha='left', va='center')
ax.text(label_x, 1, 'CURRENT ASKING PSF', weight='bold', color='#2c3e50', ha='left', va='center')

# Property Box
header_text = f"Dev: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}"
ax.text((t_low + t_high)/2, 3.4, header_text, ha='center', fontsize=12, fontweight='bold', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Value Labels
ax.text(fmv, 0.2, f'FMV\n${fmv:,.0f} PSF', ha='center', weight='bold', fontsize=11)
ax.text(our_ask, 0.2, f'OUR ASK\n${our_ask:,.0f} PSF', ha='center', weight='bold', color=status_color, fontsize=12)

# Status Title
ax.text((t_low + t_high)/2, 2.7, f"STATUS: {status_text}", fontsize=18, weight='bold', color=status_color, ha='center')

# --- LOGO ON CHART (Sharper Scaling) ---
if os.path.exists("logo.png"):
    logo_img = mpimg.imread("logo.png")
    logo_ax = fig.add_axes([0.75, 0.80, 0.18, 0.15], anchor='NE', zorder=1)
    logo_ax.imshow(logo_img, interpolation='lanczos') # Ensures sharpness
    logo_ax.axis('off')

ax.axis('off')
ax.set_ylim(-0.6, 3.7) 
ax.set_xlim(label_x - 20, max(t_high, a_high, fmv, upper_10) + 120)

st.pyplot(fig)

# --- DOWNLOAD SECTION ---
st.sidebar.divider()
st.sidebar.subheader("Download Options")
buf_png = io.BytesIO()
fig.savefig(buf_png, format="png", bbox_inches='tight', dpi=300)
st.sidebar.download_button(label="📥 Download Image (PNG)", data=buf_png.getvalue(), file_name=f"Report_{dev_name}.png", mime="image/png")

buf_pdf = io.BytesIO()
fig.savefig(buf_pdf, format="pdf", bbox_inches='tight')
st.sidebar.download_button(label="📄 Download PDF Report", data=buf_pdf.getvalue(), file_name=f"Report_{dev_name}.pdf", mime="application/pdf")
