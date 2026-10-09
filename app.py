import time
import random
import pandas as pd
import streamlit as st

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="Deriv Multi-Market Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("🎯 Deriv Multi-Market Digit & Strategy Scanner")
st.markdown("Real-time statistical tracking across 8 synthetic indices for **Matches, Differs, Even/Odd, and Over/Under** strategies.")

# --- Configuration Sidebar ---
st.sidebar.header("⚙️ Scanner Settings")
sample_size = st.sidebar.slider("Rolling Window Size (Ticks)", min_value=30, max_value=200, value=50, step=10)
refresh_speed = st.sidebar.slider("Refresh Delay (Seconds)", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
run_scanner = st.sidebar.checkbox("▶ Start Live Scanning Loop", value=False)

# --- Market Dictionary ---
MARKETS = {
    "R_10": "Volatility 10",
    "R_25": "Volatility 25",
    "R_50": "Volatility 50",
    "R_75": "Volatility 75",
    "R_100": "Volatility 100",
    "1HZ25V": "Volatility 25 (1s)",
    "1HZ75V": "Volatility 75 (1s)",
    "1HZ100V": "Volatility 100 (1s)"
}

# Initialize session state histories if not already present
if "histories" not in st.session_state:
    st.session_state.histories = {symbol: [] for symbol in MARKETS}
    for symbol in MARKETS:
        base_val = 1000 if "100" in symbol else (500 if "50" in symbol else 150)
        for _ in range(sample_size):
            mock_price = round(base_val + (random.random() * 40), 4)
            st.session_state.histories[symbol].append(int(f"{mock_price:.4f}"[-1]))

# Dashboard Layout Containers
placeholder = st.empty()

if run_scanner:
    while run_scanner:
        with placeholder.container():
            st.info(f"🔄 Live scanning active across {len(MARKETS)} markets (Window: {sample_size} ticks)...")
            
            # Create a 2-column grid layout for the 8 markets
            cols = st.columns(2)
            
            market_items = list(MARKETS.items())
            for idx, (symbol, name) in enumerate(market_items):
                col_target = cols[idx % 2]
                
                with col_target:
                    # Generate live tick simulation
                    base_val = 1000 if "100" in symbol else (500 if "50" in symbol else 150)
                    mock_price = round(base_val + (random.random() * 40), 4)
                    str_price = f"{mock_price:.4f}"
                    last_digit = int(str_price[-1])
                    
                    # Update rolling window
                    st.session_state.histories[symbol].append(last_digit)
                    if len(st.session_state.histories[symbol]) > sample_size:
                        st.session_state.histories[symbol].pop(0)
                        
                    # Frequency Calculations
                    df_digits = pd.Series(st.session_state.histories[symbol])
                    digit_counts = df_digits.value_counts().reindex(range(10), fill_value=0)
                    
                    hot_digit = digit_counts.idxmax()
                    hot_count = digit_counts.max()
                    cold_digit = digit_counts.idxmin()
                    cold_count = digit_counts.min()
                    
                    even_count = sum(digit_counts[i] for i in [0, 2, 4, 6, 8])
                    odd_count = sum(digit_counts[i] for i in [1, 3, 5, 7, 9])
                    even_pct = (even_count / sample_size) * 100
                    odd_pct = (odd_count / sample_size) * 100
                    
                    under_count = sum(digit_counts[i] for i in range(5))
                    over_count = sum(digit_counts[i] for i in range(5, 10))
                    under_pct = (under_count / sample_size) * 100
                    over_pct = (over_count / sample_size) * 100
                    
                    # Display inside an expandable card/container
                    with st.container(border=True):
                        st.markdown(f"### 📉 {name}")
                        st.text(f"Price: {mock_price} | Latest Digit: {last_digit}")
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("🔥 Hot / ❄️ Cold", f"[{hot_digit}] vs [{cold_digit}]", f"Hits: {hot_count} / {cold_count}")
                        m2.metric("Even / Odd", f"{even_pct:.0f}% / {odd_pct:.0f}%")
                        m3.metric("Under / Over", f"{under_pct:.0f}% / {over_pct:.0f}%")
                        
                        # Strategy Action Prompt
                        if cold_count <= int(sample_size * 0.04):
                            st.success(f"💡 **Differs Opportunity:** Digit [{cold_digit}] is heavily lagging ({cold_count} hits). Consider **Differs [{cold_digit}]**.")
                        elif even_pct >= 70:
                            st.success(f"💡 **Even Bias Opportunity:** Even ratio at {even_pct:.0f}%. Consider **Even** contract.")
                        elif odd_pct >= 70:
                            st.success(f"💡 **Odd Bias Opportunity:** Odd ratio at {odd_pct:.0f}%. Consider **Odd** contract.")
                            
        time.sleep(refresh_speed)
        # Rerun loop check via Streamlit rerun model if needed, or let user control via sidebar
else:
    st.warning("👈 Check **'Start Live Scanning Loop'** in the sidebar to launch the live dashboard.")
