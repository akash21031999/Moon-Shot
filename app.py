import streamlit as st
import pandas as pd
from google import genai
from google.api_core import exceptions
import yfinance as yf
import re
import time

st.set_page_config(page_title="Asymmetric Moonshot Finder", layout="wide")
st.title("🚀 Asymmetric Moonshot Finder")

# --- API KEY CHECK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

sector = st.sidebar.text_input("Enter Supply Chain Bottleneck:", "SMR Nuclear Valves")

if st.button("Research Suppliers"):
    try:
        with st.spinner("Consulting Gemini..."):
            # We use 1.5-flash as a fallback as it sometimes has more stable free quotas
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=f"Identify 3 obscure Tier 2/3 public suppliers for {sector}. End with 'TICKERS: TKR1, TKR2' format."
            )
            thesis = response.text
            st.subheader("Investment Thesis")
            st.write(thesis)

            # --- TICKER EXTRACTION ---
            tickers_match = re.search(r'TICKERS:\s*([A-Z,\s]+)', thesis)
            if tickers_match:
                tickers = [t.strip() for t in tickers_match.group(1).split(',') if t.strip()]
                
                metrics = []
                for t in tickers:
                    stock = yf.Ticker(t)
                    # Use a small delay to avoid rate limiting yfinance
                    time.sleep(0.2) 
                    info = stock.info
                    metrics.append({
                        "Ticker": t,
                        "Price": info.get('currentPrice', 'N/A'),
                        "Market Cap": info.get('marketCap', 'N/A')
                    })
                
                st.table(pd.DataFrame(metrics))

    except exceptions.ResourceExhausted as e:
        st.error("⚠️ **Quota Exceeded (429):** Your Google Cloud project likely has '0' quota. "
                 "Please ensure you have a billing account linked in the Google Cloud Console "
                 "to activate the Free Tier.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
