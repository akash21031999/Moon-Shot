import streamlit as st
import pandas as pd
from google import genai
import yfinance as yf
import re

# 1. Terminal Configuration
st.set_page_config(page_title="Supply Chain Alpha Terminal", layout="wide", page_icon="🌐")

# Center Content & Style Table
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; max-width: 900px; }
    .stTable { font-size: 14px; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Centered Search UI
st.title("🌐 Supply Chain Intelligence")
st.caption("Tier 2 & 3 Asymmetric Research Engine | March 2026")

# Centered Search Bar
with st.container():
    sector = st.text_input("ENTER INDUSTRY OR SUPPLY CHAIN BOTTLENECK:", 
                          placeholder="e.g. SMR Nuclear Valves, Neon Gas Suppliers, HBM Chip Packaging",
                          label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("RUN DEEP RESEARCH REPORT", use_container_width=True, type="primary")

# 4. Main Research Flow
if search_button and sector:
    # --- PHASE 1: SECTOR ANALYSIS ---
    with st.spinner("Analyzing Supply Chain Tiers..."):
        try:
            # Model ID updated for March 2026 stability
            MODEL_ID = "gemini-3-flash-preview" 
            
            prompt = (
                f"Perform deep research on the {sector} supply chain. "
                "1. Explain the current bottleneck or industry state. "
                "2. Identify the critical Tier 2 or Tier 3 players that actually own the IP or materials. "
                "3. Select 3 publicly traded companies (obscure small/mid caps preferred). "
                "For each company, provide a 'Thesis' and a 'Risk Factor'. "
                "At the very end of your response, strictly include: TICKERS: T1, T2, T3"
            )
            
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            report_text = response.text
            
            # Extract Tickers
            match = re.search(r'TICKERS:?\s*([\w\s,]+)', report_text, re.IGNORECASE)
            tickers = [t.strip().upper() for t in match.group(1).split(',')] if match else []

            # --- DISPLAY RESEARCH FIRST ---
            st.markdown("---")
            st.subheader(f"📑 {sector.upper()} STRATEGIC REPORT")
            st.markdown(report_text.split("TICKERS:")[0]) # Show research, hide raw ticker line

        except Exception as e:
            st.error(f"Intelligence Error: {e}")
            st.stop()

    # --- PHASE 2: ANALYST COVERAGE TABLE ---
    if tickers:
        st.subheader("📊 INSTITUTIONAL METRICS & ANALYST TARGETS")
        
        metrics_data = []
        for ticker in tickers:
            with st.spinner(f"Verifying {ticker}..."):
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Core Financials
                    price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                    target = info.get('targetMedianPrice', 'N/A')
                    rec = info.get('recommendationKey', 'N/A').replace('_', ' ').title()
                    
                    # Calculate Upside
                    upside = "N/A"
                    if isinstance(target, (int, float)) and price > 0:
                        pct = ((target - price) / price) * 100
                        upside = f"{pct:+.2f}%"

                    metrics_data.append({
                        "Ticker": ticker,
                        "Company": info.get('shortName', ticker),
                        "Current Price": f"${price:,.2f}" if price else "N/A",
                        "Analyst Target": f"${target}" if target != 'N/A' else "N/A",
                        "Projected Upside": upside,
                        "Rating": rec,
                        "Market Cap": f"${info.get('marketCap', 0)/1e9:.2f}B" if info.get('marketCap') else "N/A",
                        "PE Ratio": info.get('forwardPE', 'N/A')
                    })
                except:
                    continue

        if metrics_data:
            # Create professional table
            df = pd.DataFrame(metrics_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Mobile-friendly summary cards
            st.markdown("### Quick Insights")
            cols = st.columns(len(metrics_data))
            for i, row in enumerate(metrics_data):
                with cols[i]:
                    st.metric(row['Ticker'], row['Current Price'], row['Projected Upside'])
        else:
            st.warning("Financial data currently unavailable for these specific tickers.")

else:
    # Initial State
    st.divider()
    st.info("💡 **Institutional Tip:** Search for specific components like 'EUV Lithography Lasers' or 'Solid State Electrolyte Suppliers' for better Tier 3 results.")
