import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle
import io
from datetime import datetime, timedelta, timezone
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="ProProperty PSF Analyzer", layout="wide")

# --- CSS: CLEAN UI FOR SCREENSHOTS ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, label, .stMetric label, [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif;
    }
    /* Hide Streamlit elements for a cleaner look */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 1. Branding")
    uploaded_logo = st.file_uploader("Upload Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    st.markdown("### 2. Property Details")
    dev_name = st.text_input("Development", "Kent Ridge Hill Residences")
    unit_no  = st.text_input("Unit", "02-57")
    sqft     = st.number_input("Size (sqft)", value=1079)
    u_type   = st.text_input("Type", "3 Bedroom Premium")
    prepared_by = st.text_input("Agent Name", "James Koh")
    
    st.markdown("---")
    st.markdown("### 3. Market Data")
    # Auto-swap low/high if user enters them backwards
    t1, t2 = st.number_input("Transacted Low", value=1000), st.number_input("Transacted High", value=1200)
    t_low, t_high = min(t1, t2), max(t1, t2)
    
    a1, a2 = st.number_input("Asking Low", value=1100), st.number_input("Asking High", value=1300)
    a_low, a_high = min(a1, a2), max(a1, a2)
    
    st.markdown("### 4. Valuation")
    fmv = st.number_input("Bank/Valuation (FMV)", value=1050)
    our_ask = st.number_input("Your Asking Price", value=1100)

# --- CALCULATIONS ---
has_data = all(v is not None and v > 0 for v in [fmv, our_ask, t_high, a_high])
tz_sg = timezone(timedelta(hours=8))
today_date = datetime.now(tz_sg).strftime("%d %b %Y")

if has_data:
    lower_5, upper_5 = fmv * 0.95, fmv * 1.05
    lower_10, upper_10 = fmv * 0.90, fmv * 1.10
    diff_pct = (our_ask - fmv) / fmv
    
    # Dynamic styling based on variance
    if abs(diff_pct) <= 0.05:
        status_text, status_color = "FAIR VALUE", "#2ecc71" # Green
    elif abs(diff_pct) <= 0.10:
        status_text, status_color = "PREMIUM", "#f1c40f" # Yellow
    else:
        status_text, status_color = "ABOVE MARKET", "#e74c3c" # Red
else:
    status_text, status_color, diff_pct = "Waiting for Data...", "#7f8c8d", 0

# --- DASHBOARD LAYOUT ---
st.title(f"📍 {dev_name}")
st.caption(f"Unit: {unit_no} | Size: {sqft:,} sqft | Type: {u_type}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Valuation (FMV)", f"${fmv:,.0f} psf")
c2.metric("Your Ask", f"${our_ask:,.0f} psf")
c3.metric("Gap", f"{diff_pct:+.1%}", delta_color="inverse")
c4.metric("Total Quantum", f"${(our_ask * sqft):,.0f}")

st.divider()

# --- PLOTTING ENGINE ---
if has_data:
    # Create Figure
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('white')
    
    # Dynamic limits to prevent text cutoff
    all_values = [t_low, t_high, a_low, a_high, fmv, our_ask, lower_10, upper_10]
    data_min = min(all_values)
    data_max = max(all_values)
    data_range = data_max - data_min
    padding = data_range * 0.25 # Dynamic padding (25% of range)

    # 1. Shaded Zones (The "Safe" Zones)
    ax.axvspan(lower_10, lower_5, color='#f1c40f', alpha=0.1)  # Yellow zone
    ax.axvspan(lower_5, upper_5, color='#2ecc71', alpha=0.15)  # Green zone
    ax.axvspan(upper_5, upper_10, color='#f1c40f', alpha=0.1)  # Yellow zone

    # 2. Zone Labels
    y_labels = -1.5
    style_dict = dict(ha='center', va='top', fontsize=10, weight='bold', color='#95a5a6')
    ax.text(lower_5, y_labels, f"-5%\n${lower_5:,.0f}", **style_dict)
    ax.text(upper_5, y_labels, f"+5%\n${upper_5:,.0f}", **style_dict)
    ax.text(lower_10, y_labels - 0.7, f"-10%\n${lower_10:,.0f}", **style_dict)
    ax.text(upper_10, y_labels - 0.7, f"+10%\n${upper_10:,.0f}", **style_dict)

    # 3. Market Range Lines (Dumbbell Plot)
    # Transacted
    ax.plot([t_low, t_high], [2, 2], color='#3498db', marker='o', markersize=12, linewidth=8, solid_capstyle='round')
    # Asking
    ax.plot([a_low, a_high], [1, 1], color='#34495e', marker='o', markersize=12, linewidth=8, solid_capstyle='round')

    # 4. Labels for Lines (Dynamic placement)
    # We place text to the LEFT of the minimum value, using the calculated padding
    text_x_pos = data_min - (data_range * 0.05) 
    ax.text(text_x_pos, 2, 'RECENT TRANSACTED', weight='bold', ha='right', va='center', fontsize=12, color='#3498db')
    ax.text(text_x_pos, 1, 'MARKET ASKING', weight='bold', ha='right', va='center', fontsize=12, color='#34495e')

    # 5. The "Status" Banner
    ax.text((data_min + data_max)/2, 3.5, f"STATUS: {status_text}", fontsize=24, weight='bold', color=status_color, ha='center',
            bbox=dict(facecolor='white', edgecolor=status_color, boxstyle='round,pad=0.5', linewidth=2))

    # 6. FMV vs Ask Markers
    # FMV
    ax.scatter(fmv, 2, color='black', s=250, zorder=10, marker='D') # Diamond shape for precision
    ax.text(fmv, 2.4, f"VALUATION\n${fmv:,.0f}", ha="center", weight="bold", fontsize=11)
    
    # Our Ask
    ax.scatter(our_ask, 1, color=status_color, s=400, edgecolors='black', zorder=11, linewidth=2)
    ax.text(our_ask, 0.4, f"YOUR ASK\n${our_ask:,.0f}", ha="center", weight="bold", color=status_color, fontsize=13)

    # 7. Header / Info Block inside the chart
    # If a logo is uploaded, display it
    if uploaded_logo is not None:
        logo_img = Image.open(uploaded_logo)
        logo_ax = fig.add_axes([0.78, 0.85, 0.18, 0.10]) # Top right
        logo_ax.imshow(logo_img)
        logo_ax.axis('off')

    # Footer Info
    info_str = (f"{dev_name} ({unit_no}) | {sqft:,} sqft | {u_type}\n"
                f"Analysis by {prepared_by} | {today_date}")
    
    ax.text(0.02, 0.95, info_str, transform=fig.transFigure, ha='left', va='top', fontsize=12, fontweight='bold',
            color='#555555', bbox=dict(facecolor='#f8f9fa', edgecolor='none', boxstyle='round,pad=0.5'))

    # Final visual tweaks
    ax.axis('off')
    ax.set_ylim(-3.0, 5.0)
    ax.set_xlim(data_min - padding, data_max + (padding*0.5))
    
    # Render
    st.pyplot(fig)

    # --- DOWNLOAD BUTTON ---
    # Save plot to memory to allow downloading
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
    st.download_button(
        label="📥 Download Chart for Client",
        data=img_buffer,
        file_name=f"{dev_name}_Analysis.png",
        mime="image/png",
        use_container_width=True
    )
