import streamlit as st
import time
import pandas as pd
import pyotp
from SmartApi import SmartConnect

# Page Setup
st.set_page_config(page_title="AngelOne LIVE Trading Terminal", layout="wide")

st.title("🔴 LIVE AngelOne Market Execution Terminal")
st.caption("Direct Server Connection | Real-Time Live Prices & 5-Min Timeframe Execution")

# Sidebar - Login Credentials
st.sidebar.header("🔑 AngelOne Live Credentials")
api_key = st.sidebar.text_input("API Key", type="password")
client_code = st.sidebar.text_input("Client Code / User ID")
pin = st.sidebar.text_input("MPIN", type="password")
totp_secret = st.sidebar.text_input("TOTP Secret Key (32-digit)", type="password")

st.sidebar.divider()

# Sidebar - Asset & Order Config
st.sidebar.header("⚙️ Live Trade Setup")
exchange = st.sidebar.selectbox("Exchange", ["NSE", "MCX", "BSE"])
trading_symbol = st.sidebar.text_input("Trading Symbol (e.g. SBIN-EQ, CRUDEOIL24SEPFUT)", value="SBIN-EQ")
symbol_token = st.sidebar.text_input("Symbol Token", value="3045")

total_qty = st.sidebar.number_input("Total Order Quantity", min_value=1, value=10)
slice_size = st.sidebar.number_input("Slice Size per 5-Min", min_value=1, value=2)

# Main UI Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Exchange / Symbol", f"{exchange}: {trading_symbol}")
m2.metric("Target Quantity", total_qty)
metric_ltp = m3.empty()
metric_status = m4.empty()

metric_ltp.metric("LIVE LTP", "₹0.00")
metric_status.metric("Market Status", "OFFLINE", delta_color="off")

# Direct Connection Engine
if st.sidebar.button("⚡ Connect LIVE & Start Execution", type="primary"):
    if not (api_key and client_code and pin and totp_secret):
        st.error("❌ Sabhi AngelOne Credentials bharna zaroori hai!")
    else:
        try:
            # 1. Login to AngelOne SmartAPI
            st.info("AngelOne Live Servers se connect ho raha hai...")
            smart_api = SmartConnect(api_key=api_key)
            totp = pyotp.TOTP(totp_secret).now()
            session = smart_api.generateSession(client_code, pin, totp)
            
            if not session['status']:
                st.error(f"❌ Login Failed: {session['message']}")
            else:
                metric_status.metric("Market Status", "CONNECTED (LIVE)", delta="ONLINE")
                st.success("✅ AngelOne Live Market Connection Successful!")
                
                # 2. Live Execution Loop
                executed = 0
                slices = int(total_qty / slice_size)
                
                st.subheader("📋 Real-Time Execution Logs")
                log_box = st.empty()
                logs = []
                
                for i in range(slices):
                    # Fetch DIRECT LIVE PRICE from AngelOne
                    ltp_response = smart_api.ltpData(exchange, trading_symbol, symbol_token)
                    
                    if ltp_response and ltp_response.get('status') and ltp_response.get('data'):
                        live_price = ltp_response['data']['ltp']
                        metric_ltp.metric("LIVE LTP", f"₹{live_price}")
                        
                        # PLACE LIVE ORDER ON EXCHANGE
                        order_params = {
                            "variety": "NORMAL",
                            "tradingsymbol": trading_symbol,
                            "symboltoken": symbol_token,
                            "transactiontype": "BUY",
                            "exchange": exchange,
                            "ordertype": "MARKET",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "price": "0",
                            "quantity": str(slice_size)
                        }
                        
                        # Trigger Order to Exchange
                        order_id = smart_api.placeOrder(order_params)
                        
                        executed += slice_size
                        log_text = f"[{time.strftime('%H:%M:%S')}] 5-Min Slice {i+1}/{slices}: LIVE Buy Order Sent @ ₹{live_price} | Order ID: {order_id}"
                        logs.insert(0, log_text)
                        log_box.code("\n".join(logs), language="text")
                        
                    else:
                        st.warning("⚠️ Live price fetch karne mein issue aa raha hai. Token check karein.")
                    
                    # Wait for 5-minute candle interval (300 seconds)
                    if i < slices - 1:
                        time.sleep(300)
                        
                st.success("🎉 All Live 5-Min Slices Executed Successfully on AngelOne!")
                
        except Exception as e:
            st.error(f"🚨 System Error: {str(e)}")
