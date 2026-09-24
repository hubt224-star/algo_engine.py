import streamlit as st
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Institutional 5-Min Algo Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ 5-Minute Multi-Market Institutional Algo Terminal")
st.caption("Supports NSE, BSE & MCX Commodity Markets | Fixed 5-Min Timeframe Execution")

# Sidebar Configuration
st.sidebar.header("⚙️ Strategy & Market Setup")

# Market Segment Selection
exchange = st.sidebar.selectbox(
    "Market Segment", 
    ["NSE Equity", "NSE Derivatives (FnO)", "BSE Equity", "MCX Commodity"]
)

# Dynamic Symbol Selection based on Exchange
if exchange == "NSE Equity":
    symbols = ["RELIANCE", "HDFCBANK", "INFY", "TCS", "ICICIBANK", "SBIN", "BHARTIARTL"]
elif exchange == "NSE Derivatives (FnO)":
    symbols = ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
elif exchange == "BSE Equity":
    symbols = ["SENSEX", "BSE-SENSEX30", "TATASTEEL", "L&T"]
else:  # MCX Commodity
    symbols = ["CRUDEOIL", "GOLD", "SILVER", "NATURALGAS", "COPPER"]

symbol = st.sidebar.selectbox("Select Asset Symbol", symbols)

# Timeframe Setup (Strictly Fixed to 5-Min)
st.sidebar.info("⏱️ **Execution Timeframe:** Fixed 5-Minute Candle Close")

# Order Configuration
st.sidebar.subheader("📦 Order Setup")
order_type = st.sidebar.radio("Algo Logic", ["Iceberg Execution (5-Min)", "TWAP Slicer (5-Min)", "Supertrend/EMA Crossover (5-Min)"])
total_qty = st.sidebar.number_input("Total Quantity / Lots", min_value=1, max_value=50000, value=500)
slice_size = st.sidebar.number_input("Slice Size per 5-Min Candle", min_value=1, max_value=5000, value=50)

# Dashboard Metrics Top Banner
m1, m2, m3, m4 = st.columns(4)
m1.metric("Exchange / Asset", f"{exchange} - {symbol}")
m2.metric("Target Qty", f"{total_qty:,}")
metric_executed = m3.empty()
metric_status = m4.empty()

metric_executed.metric("Executed Qty", "0")
metric_status.metric("Engine Status", "READY", delta_color="off")

st.divider()

# Layout
col_chart, col_logs = st.columns([2, 1])

with col_chart:
    st.subheader("📈 5-Min Chart & Order Execution Stream")
    chart_placeholder = st.empty()

with col_logs:
    st.subheader("📋 Live 5-Min Candle Logs")
    log_placeholder = st.empty()

# Start Engine Button
if st.sidebar.button("🚀 Launch 5-Min Algo Engine", type="primary"):
    st.session_state.log = []
    executed = 0
    slices = int(np.ceil(total_qty / slice_size))
    
    # Base Price Simulation based on Symbol
    base_price = 2500.0 if "RELIANCE" in symbol else (6500.0 if "CRUDE" in symbol else 65000.0 if "GOLD" in symbol else 22000.0)
    
    chart_data = []

    for i in range(slices):
        remaining = total_qty - executed
        current_slice = min(slice_size, remaining)
        executed += current_slice
        
        # Simulating 5-min Candle Data
        candle_time = (datetime.now() + timedelta(minutes=i*5)).strftime("%H:%M:%S")
        base_price += np.random.uniform(-15.0, 15.0)
        
        log_entry = f"[{candle_time}] [5-MIN CLOSE] [{exchange}] {symbol} -> Executed {current_slice} Qty @ ₹{base_price:.2f}"
        st.session_state.log.insert(0, log_entry)
        
        # Update UI
        metric_executed.metric("Executed Qty", f"{executed:,}")
        metric_status.metric("Engine Status", f"CANDLE {i+1}/{slices} EXECUTED", delta="ACTIVE")
        
        # Plot Chart
        chart_data.append({"5-Min Candle": f"Candle {i+1}", "Execution Price": base_price, "Executed": executed})
        df_chart = pd.DataFrame(chart_data)
        chart_placeholder.line_chart(df_chart.set_index("5-Min Candle")["Execution Price"])
        
        # Update Logs
        log_placeholder.code("\n".join(st.session_state.log), language="text")
        
        # Simulate wait for 5-min candle interval (Fast demo simulation speed)
        time.sleep(3)
        
    metric_status.metric("Engine Status", "COMPLETED", delta="DONE")
    st.success(f"✅ Successfully executed {total_qty} units of {symbol} ({exchange}) on 5-Min Timeframe!")
