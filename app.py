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
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                  f"Focus on asymmetric moonshot bets based on recent market news. Return a brief investment thesis and list their exact stock tickers "
                  f"in a comma-separated format at the very end of your response like this: TICKERS: AAPL, MSFT, TSLA")
        
        try:
            response = model.generate_content(prompt)
            thesis = response.text
            st.subheader("LLM Supply Chain Verdict")
            st.write(thesis)
        except Exception as e:
            st.error(f"Error communicating with Gemini: {e}")
            st.stop()

    with st.spinner("Extracting Tickers and Fetching Quantitative Data via YFinance..."):
        # 2. Extract Tickers using Regex (Fixed backslashes)
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
                    info = stock.info
                    
                    # Ensure we get the price, handling different YFinance data structures
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                    
                    metrics_data.append({
                        "Ticker": ticker,
                        "Last Price": current_price,
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
                # Format the Market Cap to be more readable if it's a number
                if 'Market Cap' in df.columns:
                    df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce').apply(
                        lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
                    )
                st.dataframe(df, use_container_width=True)
            else:
                st.error("No data fetched. Please check the tickers.")
        else:
            st.error("Could not extract tickers from the LLM response. Try refining the prompt.")
