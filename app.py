import streamlit as st
import pandas as pd
from google import genai
import yfinance as yf
import re

# 1. Page Config & Styling
st.set_page_config(page_title="Moonshot Finder 2026", layout="wide", page_icon="🚀")

# Modern way to inject CSS in 2026 using st.html
st.html("""
    <style>
    .reportview-container { background: #fafafa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""")

st.title("🚀 Asymmetric Moonshot Finder")
st.caption("Tier 2/3 Supply Chain Intelligence | Powered by Gemini 3 Flash")

# 2. API Key Security
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# 3. Sidebar Inputs
st.sidebar.header("Target Sector")
sector = st.sidebar.text_input(
    "Supply Chain Bottleneck:", 
    "SMR Nuclear Valves"
)

# 4. Main Execution logic
if st.button("Run Deep Research & Valuation"):
    # --- PHASE 1: GENAI RESEARCH ---
    with st.spinner("Scanning global supply chains via Gemini..."):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # 2026 Current Model ID
            MODEL_ID = "gemini-3-flash" 
            
            prompt = (
                f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                "Provide a brief investment thesis for each. "
                "List their exact stock tickers at the very end like this: "
                "TICKERS: TICKER1, TICKER2, TICKER3"
            )
            
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            
            thesis_text = response.text
            st.subheader("💡 LLM Investment Thesis")
            st.info(thesis_text)
            
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            st.stop()

    # --- PHASE 2: DATA EXTRACTION ---
    with st.spinner("Extracting market data..."):
        # Robust Regex to catch tickers
        tickers_match = re.search(r'TICKERS:?\s*([\w\s,]+)', thesis_text, re.IGNORECASE)
        
        if tickers_match:
            raw_string = tickers_match.group(1)
            tickers = [t.strip().upper() for t in raw_string.split(',') if t.strip()]
            
            metrics_list = []
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Fetching core metrics
                    price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                    mkt_cap = info.get('marketCap', 0)
                    
                    metrics_list.append({
                        "Ticker": ticker,
                        "Company": info.get('longName', 'Unknown'),
                        "Price": price,
                        "Market Cap": mkt_cap,
                        "Forward P/E": info.get('forwardPE', 'N/A'),
                        "Volume": info.get('regularMarketVolume', 'N/A')
                    })
                except:
                    continue 

            # --- PHASE 3: DASHBOARD DISPLAY ---
            if metrics_list:
                st.subheader("📊 Real-Time Market Metrics")
                df = pd.DataFrame(metrics_list)
                
                # Format Market Cap for human eyes
                def format_mkt_cap(num):
                    if not isinstance(num, (int, float)) or num == 0: return "N/A"
                    if num >= 1e9: return f"${num/1e9:.2f}B"
                    return f"${num/1e6:.2f}M"
                
                df['Market Cap'] = df['Market Cap'].apply(format_mkt_cap)
                df['Price'] = df['Price'].apply(lambda x: f"${x:,.2f}" if x > 0 else "N/A")
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error("No financial data found. The AI might have suggested invalid tickers.")
        else:
            st.error("Could not parse tickers. Try running the research again.")

st.divider()
st.caption("AI-generated insights. Verify all tickers before trading.")
