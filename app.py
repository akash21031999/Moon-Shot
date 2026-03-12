import streamlit as st
import pandas as pd
from google import genai
import yfinance as yf
import re

# 1. Page Config
st.set_page_config(page_title="Moonshot Finder 2026", layout="wide", page_icon="🚀")

# Modern CSS injection
st.html("""
    <style>
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    </style>
""")

st.title("🚀 Asymmetric Moonshot Finder")
st.caption("Tier 2/3 Supply Chain Intelligence | March 2026 Edition")

# 2. API Key Security
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# 3. Sidebar Inputs
st.sidebar.header("Research Parameters")
sector = st.sidebar.text_input("Supply Chain Bottleneck:", "AI Data Center Cooling")

# 4. Main Logic
if st.button("Generate Alpha Report"):
    # --- PHASE 1: GENAI RESEARCH ---
    with st.spinner("Analyzing global supply chains..."):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Using the STABLE alias to prevent 404 errors
            # gemini-2.5-flash is currently the production-stable version
            MODEL_ID = "gemini-2.5-flash" 
            
            prompt = (
                f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                "Focus on small-cap companies with asymmetric upside. "
                "Format your response with a thesis for each, and end exactly with: "
                "TICKERS: TICKER1, TICKER2, TICKER3"
            )
            
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            
            thesis_text = response.text
            st.subheader("💡 Investment Thesis")
            st.info(thesis_text)
            
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            st.stop()

    # --- PHASE 2: DATA EXTRACTION & YFINANCE ---
    with st.spinner("Fetching real-time market data..."):
        # Improved Regex to find tickers after the keyword 'TICKERS:'
        match = re.search(r'TICKERS:?\s*([\w\s,.]+)', thesis_text, re.IGNORECASE)
        
        if match:
            raw_list = match.group(1).replace('.', '').split(',')
            tickers = [t.strip().upper() for t in raw_list if t.strip()]
            
            metrics = []
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    # We use a 2-second timeout for info to keep the app snappy
                    info = stock.info
                    
                    price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                    mkt_cap = info.get('marketCap', 0)
                    
                    metrics.append({
                        "Ticker": ticker,
                        "Company": info.get('longName', 'Unknown'),
                        "Price": price,
                        "Market Cap": mkt_cap,
                        "Div Yield": info.get('dividendYield', 0),
                        "Volume": info.get('regularMarketVolume', 0)
                    })
                except:
                    continue

            if metrics:
                st.subheader("📊 Quantitative Snapshot")
                df = pd.DataFrame(metrics)
                
                # Cleanup formatting
                def format_mkt_cap(val):
                    if val >= 1e9: return f"${val/1e9:.2f}B"
                    if val >= 1e6: return f"${val/1e6:.2f}M"
                    return "N/A"

                df['Market Cap'] = df['Market Cap'].apply(format_mkt_cap)
                df['Price'] = df['Price'].apply(lambda x: f"${x:,.2f}" if x > 0 else "N/A")
                df['Div Yield'] = df['Div Yield'].apply(lambda x: f"{x*100:.2f}%" if x else "0%")

                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Could not find market data for the suggested tickers.")
        else:
            st.error("The AI didn't provide tickers in the requested format. Please try again.")

st.divider()
st.caption("Financial Disclaimer: For educational use only. Verify all data via official exchange filings.")
