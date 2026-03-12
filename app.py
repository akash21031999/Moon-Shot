import streamlit as st
import pandas as pd
from google import genai
import yfinance as yf
import re

# Set page configuration
st.set_page_config(page_title="Asymmetric Moonshot Finder", layout="wide", page_icon="🚀")

st.title("🚀 Asymmetric Moonshot Finder: Tier 2/3 Supply Chain")

# --- API KEY CHECK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add your 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Framework Settings")
sector = st.sidebar.text_input(
    "Enter Supply Chain Bottleneck (e.g., SMR Nuclear Valves, AI Data Center Cooling):", 
    "SMR Nuclear Valves"
)

# --- RESEARCH ENGINE ---
if st.button("Research Suppliers & Extract Metrics"):
    with st.spinner(f"Analyzing {sector} using Google Gemini..."):
        try:
            # Initialize the new GenAI client
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            prompt = (
                f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                "Focus on asymmetric moonshot bets based on recent market news. "
                "Return a brief investment thesis for each and list their exact stock tickers "
                "in a comma-separated format at the very end of your response like this: TICKERS: AAPL, MSFT, TSLA"
            )
            
            # Use the correct model name (e.g., gemini-2.0-flash or gemini-1.5-flash)
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            
            thesis = response.text
            st.subheader("LLM Supply Chain Verdict")
            st.info(thesis)
            
        except Exception as e:
            st.error(f"Error communicating with Gemini: {e}")
            st.stop()

    with st.spinner("Extracting Tickers and Fetching Quantitative Data..."):
        # Extract Tickers using Regex
        # Looking for the pattern "TICKERS: TICKER1, TICKER2"
        tickers_match = re.search(r'TICKERS:\s*([A-Z0-9,\s\.]+)', thesis, re.IGNORECASE)
        
        if tickers_match:
            raw_tickers = tickers_match.group(1).split(',')
            tickers = [t.strip().upper() for t in raw_tickers if t.strip()]
            
            metrics_data = []
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Handle price variations in yfinance dictionary
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 'N/A')
                    
                    metrics_data.append({
                        "Ticker": ticker,
                        "Name": info.get('longName', 'N/A'),
                        "Last Price": current_price,
                        "Market Cap": info.get('marketCap', 'N/A'),
                        "Trailing P/E": info.get('trailingPE', 'N/A'),
                        "Volume": info.get('volume', 'N/A')
                    })
                except Exception as e:
                    st.warning(f"Could not fetch data for {ticker}: {e}")
            
            if metrics_data:
                st.subheader("Quantitative Metrics (Real-Time)")
                df = pd.DataFrame(metrics_data)
                
                # Format Market Cap for readability
                if 'Market Cap' in df.columns:
                    df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce').apply(
                        lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
                    )
                
                st.dataframe(df, use_container_width=True)
            else:
                st.error("No quantitative data could be retrieved for the extracted tickers.")
        else:
            st.error("Could not find tickers in the response. Ensure the LLM followed the 'TICKERS:' format.")
