import streamlit as st
import time
import pandas as pd
import pyotp
from SmartApi import SmartConnect

# Page Setup
st.set_page_config(page_title="AngelOne Live Market Tracker", layout="wide")

st.title("📊 LIVE Market Data Tracker (No Trade Mode)")
st.caption("Direct Server Connection | Only Real-Time Price Tracking & 5-Min Intervals")

# Load Credentials Automatically from Secrets
try:
    API_KEY = st.secrets["API_KEY"]
    CLIENT_CODE = st.secrets["CLIENT_CODE"]
    PIN = st.secrets["PIN"]
    TOTP_SECRET = st.secrets["TOTP_SECRET"]
    CREDENTIALS_FOUND = True
except Exception:
    CREDENTIALS_FOUND = False

# Sidebar Controls
st.sidebar.header("⚙️ Market Data Setup")
exchange = st.sidebar.selectbox("Exchange", ["NSE", "MCX", "BSE"])
trading_symbol = st.sidebar.text_input("Symbol (e.g. SBIN-EQ, CRUDEOIL24SEPFUT, GOLD)", value="SBIN-EQ")
symbol_token = st.sidebar.text_input("Symbol Token", value="3045")

refresh_rate = st.sidebar.slider("Price Refresh Interval (Seconds)", min_value=1, max_value=300, value=5)

# Metrics UI
m1, m2, m3 = st.columns(3)
m1.metric("Selected Asset", f"{exchange}: {trading_symbol}")
metric_ltp = m2.empty()
metric_status = m3.empty()

metric_ltp.metric("LIVE LTP", "₹0.00")

if not CREDENTIALS_FOUND:
    metric_status.metric("Market Status", "CREDENTIALS MISSING", delta_color="off")
    st.error("⚠️ Streamlit Secrets mein Credentials nahi hain. App Settings -> Secrets mein daalein.")
else:
    metric_status.metric("Market Status", "READY TO TRACK", delta="ONLINE")

st.divider()

col_chart, col_logs = st.columns([2, 1])

with col_chart:
    st.subheader("📈 Live Price Movement Chart")
    chart_box = st.empty()

with col_logs:
    st.subheader("📋 5-Min Price Feed Logs")
    log_box = st.empty()

# Start Tracking Button
if st.sidebar.button("📡 Connect Live Feed", type="primary"):
    if not CREDENTIALS_FOUND:
        st.error("Pehle Streamlit Settings mein credentials save karein.")
    else:
        try:
            st.info("AngelOne Live Market Feed se connect kar rahe hain...")
            smart_api = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            session = smart_api.generateSession(CLIENT_CODE, PIN, totp)

            if not session.get('status'):
                st.error(f"❌ Login Failed: {session.get('message')}")
            else:
                metric_status.metric("Market Status", "LIVE STREAMING", delta="ACTIVE")
                st.success("✅ Connected to AngelOne Live Market Data!")

                price_history = []
                logs = []

                # Infinite/Continuous Price Tracker Loop
                while True:
                    # FETCH DIRECT LIVE PRICE FROM ANGELONE (NO ORDERS PLACED)
                    ltp_response = smart_api.ltpData(exchange, trading_symbol, symbol_token)

                    if ltp_response and ltp_response.get('status') and ltp_response.get('data'):
                        live_price = float(ltp_response['data']['ltp'])
                        current_time = time.strftime('%H:%M:%S')

                        metric_ltp.metric("LIVE LTP", f"₹{live_price:.2f}")

                        # Update Chart Data
                        price_history.append({"Time": current_time, "Price": live_price})
                        df_chart = pd.DataFrame(price_history)
                        chart_box.line_chart(df_chart.set_index("Time")["Price"])

                        # Log Entry
                        log_text = f"[{current_time}] {exchange}:{trading_symbol} -> Live LTP: ₹{live_price:.2f}"
                        logs.insert(0, log_text)
                        log_box.code("\n".join(logs[:15]), language="text")

                    else:
                        st.warning("⚠️ Live price receive nahi ho pa raha. Token check karein.")

                    time.sleep(refresh_rate)

        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
