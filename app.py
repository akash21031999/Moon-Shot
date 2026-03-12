import streamlit as st
import pandas as pd
from openai import OpenAI
from openbb import obb
import re

# Set page configuration
st.set_page_config(page_title="Asymmetric Moonshot Finder", layout="wide")
st.title("🚀 Asymmetric Moonshot Finder: Tier 2/3 Supply Chain")

# Safely load API Keys from Streamlit Secrets
PERPLEXITY_API_KEY = st.secrets["PERPLEXITY_API_KEY"]

st.sidebar.header("Framework Settings")
sector = st.sidebar.text_input("Enter Supply Chain Bottleneck (e.g., SMR Nuclear Valves, AI Data Center Cooling):", "SMR Nuclear Valves")

if st.button("Research Suppliers & Extract Metrics"):
    with st.spinner(f"Analyzing {sector} using Perplexity..."):
        # 1. Qualitative Research via Perplexity API
        client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
        prompt = (f"Identify 3 obscure, publicly traded Tier 2 or Tier 3 suppliers for {sector}. "
                  f"Focus on asymmetric moonshot bets. Return a brief investment thesis and list their exact stock tickers "
                  f"in a comma-separated format at the very end of your response like this: TICKERS: AAPL, MSFT, TSLA")
        
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}]
        )
        thesis = response.choices[0].message.content
        st.subheader("LLM Supply Chain Verdict")
        st.write(thesis)

    with st.spinner("Extracting Tickers and Fetching Quantitative Data via OpenBB..."):
        # 2. Extract Tickers using Regex
        tickers_match = re.search(r'TICKERS:\s*([A-Z,\s]+)', thesis)
        if tickers_match:
            raw_tickers = tickers_match.group(1).split(',')
            tickers = [t.strip() for t in raw_tickers if t.strip()]
            
            # 3. Fetch OpenBB Quantitative Data
            metrics_data = []
            for ticker in tickers:
                try:
                    # OpenBB V4 syntax for equity quotes
                    quote = obb.equity.price.quote(symbol=ticker, provider="yfinance").to_df()
                    if not quote.empty:
                        metrics_data.append({
                            "Ticker": ticker,
                            "Last Price": quote['last_price'].iloc[0],
                            "Volume": quote['volume'].iloc[0],
                            "Day High": quote['day_high'].iloc[0],
                            "Day Low": quote['day_low'].iloc[0]
                        })
                except Exception as e:
                    st.warning(f"Could not fetch data for {ticker}: {e}")
            
            # 4. Display Results in a Dashboard Table
            if metrics_data:
                st.subheader("Quantitative Metrics (Real-Time)")
                df = pd.DataFrame(metrics_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.error("Could not extract tickers from the LLM response. Try refining the prompt.")
