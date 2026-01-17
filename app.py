import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone

# Page Configuration
st.set_page_config(page_title="Property PSF Analyzer", layout="wide")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Property Details")
dev_name = st.sidebar.text_input("Development Name", "KRHR")
unit_no  = st.sidebar.text_input("Unit Number", "02-57")
sqft     = st.sidebar.text_input("Size (sqft)", "1079")
u_type   = st.sidebar.text_input("Unit Type", "3 Room")

st.sidebar.header("2. Market Data")
t_low  = st.sidebar.number_input("Lowest Transacted PSF", value=1000)
t_high = st.sidebar.number_input("Highest Transacted PSF", value=1200)
a_low  = st.sidebar.number_input("Lowest Asking PSF", value=1050)
a_high = st.sidebar.number_input("Highest Asking PSF", value=1300)
fmv    = st.sidebar.number_input("Fair Market Value (FMV)", value=1150)
my_ask = st.sidebar.number_input("Your Current Asking PSF", value=1250)

# --- CALCULATIONS ---
lower_5, upper_5 = fmv * 0.95, fmv * 1.05
lower_10, upper_10 = fmv * 0.90, fmv * 1.10
diff_pct = abs(my_ask - fmv) / fmv

if diff_pct <= 0.05:
    status_text, status_color = "WITHIN 5% OF FMV (GOOD VALUE)", "#2ecc71"
elif diff_pct <= 0.10:
    status_text, status_color = "5% - 10% ABOVE FMV (PREMIUM)", "#f1c40f"
else:
    status_text, status_color = "OVER 10% ABOVE FMV (HIGH PREMIUM)", "#e74c3c"

tz_sg = timezone(timedelta(hours=8))
gen_time = datetime.now(tz_sg).strftime("%d %b %Y, %H:%M (GMT+8)")

# --- PLOTTING ---
fig, ax = plt.subplots(figsize=(15, 8))
ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.15)
ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.15)
ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.15)

y_trans, y_ask = 2, 1
ax.plot([t_low, t_high], [y_trans, y_trans], color='#1f77b4', marker='o', linewidth=5)
ax.plot([a_low, a_high], [y_ask, y_ask], color='#34495e', marker='o', linewidth=5)
ax.plot(fmv, y_trans, marker='o', color='black', markersize=10)
ax.plot([fmv, fmv], [y_trans, 0.4], color='grey', linestyle='--', alpha=0.4)
ax.plot(my_ask, y_ask, marker='o', color=status_color, markersize=12, markeredgecolor='black')
ax.plot([my_ask, my_ask], [y_ask, 0.4], color=status_color, linestyle='--', linewidth=2)

# Text Elements
header = f"Dev: {dev_name}  |  Unit: {unit_no}  |  Size: {sqft} sqft  |  Type: {u_type}"
ax.text((t_low + t_high)/2, 3.4, header, ha='center', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
ax.text(min(t_low, a_low, fmv) - 60, y_trans, 'TRANSACTED', ha='right', va='center', fontweight='bold', color='#1f77b4')
ax.text(min(t_low, a_low, fmv) - 60, y_ask, 'ASKING', ha='right', va='center', fontweight='bold', color='#34495e')
ax.text(fmv, 0.2, f'FMV\n${int(fmv)}', ha='center', fontweight='bold')
ax.text(my_ask, 0.2, f'MY ASK\n${int(my_ask)}', ha='center', fontweight='bold', color=status_color)
ax.text((t_low + t_high)/2, 2.8, f"ANALYSIS: {status_text}", ha='center', fontsize=14, fontweight='bold', color=status_color)
ax.text((t_low + t_high)/2, -0.2, f"Report Generated: {gen_time}", ha='center', fontsize=9, color='grey', fontstyle='italic')

ax.axis('off')
ax.set_ylim(-0.4, 3.7)

# Display in Streamlit
st.pyplot(fig)