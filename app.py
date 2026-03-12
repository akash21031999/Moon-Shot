import streamlit as st
import pandas as pd
from google import genai
import yfinance as yf
import re
import plotly.graph_objects as go

# 1. Terminal Styling (Dark Mode & High Density)
st.set_page_config(page_title="ALPHA TERMINAL v3", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1a1c24; border: 1px solid #30363d; padding: 15px; border-radius: 5px; }
    .stDataFrame { border: 1px solid #30363d; }
    .stButton>button { width: 100%; border-radius: 2px; background-color: #21262d; border: 1px solid #30363d; color: #58a6ff; }
    .stButton>button:hover { border-color: #58a6ff; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("MISSING API KEY")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Sidebar (Search & Filter)
with st.sidebar:
    st.title("🗄️ TERMINAL CTL")
    sector_input = st.text_input("STRATEGY FOCUS:", "AI Power Grid Hardware")
    st.divider()
    model_choice = st.selectbox("LLM ENGINE", ["gemini-2.5-flash", "gemini-3-flash-preview"])
    st.caption("v3.2.0-stable | Build: 2026.03")

# 4. Main Header
st.title("⚡ ALPHA TERMINAL: SUPPLY CHAIN INTELLIGENCE")

# 5. Core Execution logic
if st.button("EXECUTE DEEP RESEARCH"):
    # --- PHASE 1: QUALITATIVE INTELLIGENCE ---
    with st.spinner("QUERYING GLOBAL SUPPLY CHAIN DATA..."):
        try:
            prompt = (
                f"Identify 3 publicly traded companies that are critical but obscure Tier 2/3 suppliers for {sector_input}. "
                "Provide a professional 'Institutional Note' for each. "
                "At the end, provide exactly: TICKERS: T1, T2, T3"
            )
            response = client.models.generate_content(model=model_choice, contents=prompt)
            raw_text = response.text
            
            # Extract Tickers
            match = re.search(r'TICKERS:?\s*([\w\s,]+)', raw_text, re.IGNORECASE)
            tickers = [t.strip().upper() for t in match.group(1).split(',')] if match else []
            
            # Display Research Note
            with st.expander("📝 VIEW INSTITUTIONAL RESEARCH NOTE", expanded=True):
                st.write(raw_text)
                
        except Exception as e:
            st.error(f"RESEARCH_FAILURE: {e}")
            st.stop()

    # --- PHASE 2: QUANTITATIVE DASHBOARD ---
    if tickers:
        st.subheader("📊 QUANTITATIVE OVERVIEW")
        
        # We loop through tickers and show them in a mobile-friendly grid
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1mo")
                
                # Header for each company
                st.divider()
                col_title, col_price = st.columns([3, 1])
                with col_title:
                    st.header(f"{ticker}: {info.get('longName', 'N/A')}")
                with col_price:
                    price = info.get('currentPrice', 0)
                    change = info.get('regularMarketChangePercent', 0)
                    st.metric("PRICE", f"${price:.2f}", f"{change:.2f}%")

                # Bloomberg-style Key Ratios
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MKT CAP", f"${info.get('marketCap', 0)/1e9:.2f}B")
                c2.metric("FWD P/E", info.get('forwardPE', 'N/A'))
                c3.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%")
                c4.metric("D/E RATIO", info.get('debtToEquity', 'N/A'))

                # mini Chart (Plotly)
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'],
                    increasing_line_color='#58a6ff', decreasing_line_color='#f78166'
                )])
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), template="plotly_dark", xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.warning(f"SKIP {ticker}: Market Data Timeout")

else:
    # Landing State
    st.info("System Ready. Input a sector in the left panel and click 'Execute' to begin research.")

st.divider()
st.caption("CONFIDENTIAL | FOR INSTITUTIONAL USE ONLY | DATA DELAYED 15M")
