import streamlit as st
import time
import pandas as pd
import pyotp
from SmartApi import SmartConnect

# Page Setup
st.set_page_config(page_title="AngelOne Multi-Segment Live Tracker", layout="wide")

st.title("📊 LIVE Market Tracker (NSE, BSE, MCX, FnO)")
st.caption("Direct Server Connection | Real-Time Price Tracking & 5-Min Intervals")

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

# Expanded Exchange Selection
exchange = st.sidebar.selectbox("Exchange Segment", ["NFO (NSE FnO)", "BFO (BSE FnO)", "NSE (Equity)", "BSE (Equity)", "MCX (Commodity)"])

# Dynamic Symbol Setup based on Exchange
if exchange == "NFO (NSE FnO)":
    symbols_preset = {"NIFTY 26SEP24 FUT": "12345", "BANKNIFTY 26SEP24 FUT": "67890", "FINNIFTY 26SEP24 FUT": "11223"}
    default_symbol = "NIFTY26SEPFUT"
    default_token = "12345"
    api_exchange = "NFO"
elif exchange == "BFO (BSE FnO)":
    symbols_preset = {"SENSEX 26SEP24 FUT": "99887", "BANKEX 26SEP24 FUT": "77665"}
    default_symbol = "BSX26SEPFUT"
    default_token = "99887"
    api_exchange = "BFO"
elif exchange == "NSE (Equity)":
    default_symbol = "SBIN-EQ"
    default_token = "3045"
    api_exchange = "NSE"
elif exchange == "BSE (Equity)":
    default_symbol = "SENSEX"
    default_token = "500112"
    api_exchange = "BSE"
else:  # MCX Commodity
    default_symbol = "CRUDEOIL24SEPFUT"
    default_token = "288509"
    api_exchange = "MCX"

trading_symbol = st.sidebar.text_input("Trading Symbol", value=default_symbol)
symbol_token = st.sidebar.text_input("Symbol Token", value=default_token)

refresh_rate = st.sidebar.slider("Price Refresh Interval (Seconds)", min_value=1, max_value=300, value=5)

# Metrics UI
m1, m2, m3 = st.columns(3)
m1.metric("Selected Asset", f"{api_exchange}: {trading_symbol}")
metric_ltp = m2.empty()
metric_status = m3.empty()

metric_ltp.metric("LIVE LTP", "₹0.00")

if not CREDENTIALS_FOUND:
    metric_status.metric("Market Status", "CREDENTIALS MISSING", delta_color="off")
    st.error("⚠️ Streamlit Secrets mein Credentials nahi hain.")
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

# Start Tracking
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
                st.success(f"✅ Connected to AngelOne ({api_exchange}) Live Market Data!")

                price_history = []
                logs = []

                while True:
                    # FETCH LIVE PRICE FROM ANGELONE (NO TRADES)
                    ltp_response = smart_api.ltpData(api_exchange, trading_symbol, symbol_token)

                    if ltp_response and ltp_response.get('status') and ltp_response.get('data'):
                        live_price = float(ltp_response['data']['ltp'])
                        current_time = time.strftime('%H:%M:%S')

                        metric_ltp.metric("LIVE LTP", f"₹{live_price:.2f}")

                        # Update Chart
                        price_history.append({"Time": current_time, "Price": live_price})
                        df_chart = pd.DataFrame(price_history)
                        chart_box.line_chart(df_chart.set_index("Time")["Price"])

                        # Update Logs
                        log_text = f"[{current_time}] {api_exchange}:{trading_symbol} -> Live LTP: ₹{live_price:.2f}"
                        logs.insert(0, log_text)
                        log_box.code("\n".join(logs[:15]), language="text")

                    else:
                        st.warning("⚠️ Live price fetch nahi ho pa raha. Token ya Symbol Token check karein.")

                    time.sleep(refresh_rate)

        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
