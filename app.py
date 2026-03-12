import streamlit as st
import pandas as pd
import google.generativeai as genai
import yfinance as yf
import re

# Set page configuration
st.set_page_config(page_title="Asymmetric Moonshot Finder", layout="wide")
st.title("🚀 Asymmetric Moonshot Finder: Tier 2/3 Supply Chain")

# Safely load API Keys from Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

st.sidebar.header("Framework Settings")
sector = st.sidebar.text_input("Enter Supply Chain Bottleneck (e.g., SMR Nuclear Valves, AI Data Center Cooling):", "SMR Nuclear Valves")

if st.button("Research Suppliers & Extract Metrics"):
    with st.spinner(f"Analyzing {sector} using Google Gemini..."):
        # 1. Qualitative Research via Google Gemini API
        model = genai.GenerativeModel('gemini-pro')
        prompt = (f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                  f"Focus on asymmetric moonshot bets. Return a brief investment thesis and list their exact stock tickers "
                  f"in a comma-separated format at the very end of your response like this: TICKERS: AAPL, MSFT, TSLA")
        
        response = model.generate_content(prompt)
        thesis = response.text
        st.subheader("LLM Supply Chain Verdict")
        st.write(thesis)

    with st.spinner("Extracting Tickers and Fetching Quantitative Data via YFinance..."):
        # 2. Extract Tickers using Regex
        tickers_match = re.search(r'TICKERS:\s*([A-Z,\s]+)', thesis)
        if tickers_match:
            raw_tickers = tickers_match.group(1).split(',')
            tickers = [t.strip() for t in raw_tickers if t.strip()]
            
            # 3. Fetch YFinance Quantitative Data
            metrics_data = []
            for ticker in tickers:
                try:
                    # YFinance data fetching
                    stock = yf.Ticker(ticker)
                    history = stock.history(period="1d")
                    info = stock.info
                    
                    if not history.empty:
                        metrics_data.append({
                            "Ticker": ticker,
                            "Last Price": info.get('currentPrice', 'N/A'),
                            "Volume": info.get('volume', 'N/A'),
                            "Day High": info.get('dayHigh', 'N/A'),
                            "Day Low": info.get('dayLow', 'N/A'),
                            "Market Cap": info.get('marketCap', 'N/A')
                        })
                except Exception as e:
                    st.warning(f"Could not fetch data for {ticker}: {e}")
            
            # 4. Display Results in a Dashboard Table
            if metrics_data:
                st.subheader("Quantitative Metrics (Real-Time)")
                df = pd.DataFrame(metrics_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.error("No data fetched. Please check the tickers.")
        else:
            st.error("Could not extract tickers from the LLM response. Try refining the prompt.")
