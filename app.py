import streamlit as st
import pandas as pd
from google import genai
import yfinance as yf
import re

# 1. Page Config & Styling
st.set_page_config(page_title="Moonshot Finder 2026", layout="wide", page_icon="🚀")
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🚀 Asymmetric Moonshot Finder")
st.caption("Tier 2/3 Supply Chain Intelligence powered by Gemini 3 Flash")

# 2. API Key Security
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# 3. Sidebar Inputs
st.sidebar.header("Target Sector")
sector = st.sidebar.text_input(
    "Supply Chain Bottleneck:", 
    "High-Density AI Cooling Systems"
)
st.sidebar.info("Tip: Try 'SMR Nuclear Valves' or 'Gallium Nitride Foundries'.")

# 4. Main Execution logic
if st.button("Run Deep Research & Valuation"):
    # --- PHASE 1: GENAI RESEARCH ---
    with st.spinner("Scanning global supply chains via Gemini..."):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Updated to the latest 2026 Model ID
            MODEL_ID = "gemini-3-flash" 
            
            prompt = (
                f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                "Provide a 2-sentence investment thesis for each focusing on 'asymmetric upside'. "
                "Include their exact stock tickers at the end of your response exactly like this: "
                "TICKERS: [TICKER1], [TICKER2], [TICKER3]"
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

    # --- PHASE 2: DATA EXTRACTION ---
    with st.spinner("Extracting market data..."):
        # Improved Regex to catch tickers even if they have brackets or extra spaces
        tickers_match = re.search(r'TICKERS:?\s*([\w\s,\[\]\.]+)', thesis_text, re.IGNORECASE)
        
        if tickers_match:
            # Clean up the string: remove brackets, spaces, and split by comma
            raw_string = tickers_match.group(1).replace('[', '').replace(']', '')
            tickers = [t.strip().upper() for t in raw_string.split(',') if t.strip()]
            
            metrics_list = []
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    # Use fast_info or info (info is more comprehensive)
                    info = stock.info
                    
                    # Valuation & Price Logic
                    price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                    mkt_cap = info.get('marketCap', 0)
                    
                    metrics_list.append({
                        "Ticker": ticker,
                        "Company": info.get('longName', 'Unknown'),
                        "Price": price,
                        "Market Cap": mkt_cap,
                        "P/E (Forward)": info.get('forwardPE', 'N/A'),
                        "52W High": info.get('fiftyTwoWeekHigh', 'N/A'),
                        "Volume": info.get('regularMarketVolume', 'N/A')
                    })
                except Exception:
                    continue # Skip tickers that yfinance can't find

            # --- PHASE 3: DASHBOARD DISPLAY ---
            if metrics_list:
                st.subheader("📊 Real-Time Market Metrics")
                df = pd.DataFrame(metrics_list)
                
                # Professional Formatting
                if not df.empty:
                    # Format Price as Currency
                    df['Price'] = df['Price'].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
                    
                    # Format Market Cap as readable Billions/Millions
                    def format_currency(num):
                        if not isinstance(num, (int, float)) or num == 0: return "N/A"
                        if num >= 1e9: return f"${num/1e9:.2f}B"
                        return f"${num/1e6:.2f}M"
                    
                    df['Market Cap'] = df['Market Cap'].apply(format_currency)
                    
                    st.table(df) # Static table looks cleaner for small stock lists
                else:
                    st.warning("No financial data found for the identified tickers.")
            else:
                st.error("The LLM suggested tickers, but they couldn't be parsed. Try again.")
        else:
            st.error("Could not find the 'TICKERS:' tag in the LLM response.")

st.divider()
st.caption("Note: AI can hallucinate tickers. Always verify symbols before making financial decisions.")
