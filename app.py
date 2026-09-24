import streamlit as st
import time
import pandas as pd
import numpy as np

# Page Layout Setup
st.set_page_config(page_title="Institutional Algo Terminal", layout="wide")

st.title("⚡ Institutional Algo Execution Engine")
st.caption("Powered by Streamlit & Python Low-Latency Logic")

# Sidebar Configuration
st.sidebar.header("🕹️ Order Execution Panel")
symbol = st.sidebar.selectbox("Select Asset", ["RELIANCE", "INFY", "TCS", "HDFCBANK", "NIFTY50"])
total_qty = st.sidebar.number_input("Total Quantity", min_value=10, max_value=100000, value=2000, step=100)
slice_size = st.sidebar.number_input("Slice Size (Iceberg)", min_value=5, max_value=10000, value=200, step=50)
interval = st.sidebar.slider("Execution Delay (Seconds)", min_value=1, max_value=30, value=2)

algo_type = st.sidebar.radio("Algo Strategy", ["Iceberg Order", "TWAP Execution", "VWAP Slicer"])

# Session State for Live Tracking
if "running" not in st.session_state:
    st.session_state.running = False
if "log" not in st.session_state:
    st.session_state.log = []

# Main Dashboard Cards
col1, col2, col3, col4 = st.columns(4)
metric_qty = col1.empty()
metric_executed = col2.empty()
metric_progress = col3.empty()
metric_status = col4.empty()

# Initial Metrics Display
metric_qty.metric("Total Target Qty", f"{total_qty:,}")
metric_executed.metric("Executed Qty", "0")
metric_progress.metric("Progress", "0%")
metric_status.metric("Engine Status", "IDLE", delta_color="off")

st.divider()

# Layout: Chart on Left, Live Logs on Right
chart_col, log_col = st.columns([2, 1])

with chart_col:
    st.subheader("📈 Real-Time Execution Tracking")
    chart_placeholder = st.empty()

with log_col:
    st.subheader("📝 Order Execution Logs")
    log_placeholder = st.empty()

# Start Button Control
start_btn = st.sidebar.button("🚀 Start Algo Execution", type="primary")

if start_btn:
    st.session_state.running = True
    st.session_state.log = []
    
    executed = 0
    slices = int(np.ceil(total_qty / slice_size))
    
    # Dummy price for simulation
    current_price = 2500.0
    execution_data = []

    for i in range(slices):
        if not st.session_state.running:
            break
            
        remaining = total_qty - executed
        current_slice = min(slice_size, remaining)
        executed += current_slice
        
        # Price slight fluctuation (Simulating live market)
        current_price += np.random.uniform(-1.5, 1.5)
        
        # Log message
        log_entry = f"[{time.strftime('%H:%M:%S')}] Executed Slice {i+1}/{slices}: {current_slice} shares @ ₹{current_price:.2f}"
        st.session_state.log.insert(0, log_entry)
        
        # Update Dashboard Metrics
        metric_qty.metric("Total Target Qty", f"{total_qty:,}")
        metric_executed.metric("Executed Qty", f"{executed:,}")
        progress_pct = (executed / total_qty) * 100
        metric_progress.metric("Progress", f"{progress_pct:.1f}%")
        metric_status.metric("Engine Status", "EXECUTING", delta="RUNNING")
        
        # Update Execution Chart
        execution_data.append({"Slice": i+1, "Price": current_price, "Executed_Qty": executed})
        df_chart = pd.DataFrame(execution_data)
        chart_placeholder.line_chart(df_chart.set_index("Slice")["Price"])
        
        # Update Logs
        log_placeholder.code("\n".join(st.session_state.log[:10]), language="text")
        
        time.sleep(interval)
        
    st.session_state.running = False
    metric_status.metric("Engine Status", "COMPLETED", delta="DONE")
    st.success("✅ Algo Execution Completed Successfully!")

