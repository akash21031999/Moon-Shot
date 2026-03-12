import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import yfinance as yf
import re

# 1. Page Configuration & Theme
st.set_page_config(page_title="ALPHA TERMINAL v5", layout="wide", page_icon="🏦")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #05070a; color: #00ffaa; font-family: 'Roboto Mono', monospace; }
    .stMetric { background: #0c1015; border: 1px solid #1f2937; padding: 15px; border-radius: 4px; }
    .report-box { background: #0c1015; border: 1px solid #1f2937; padding: 25px; border-radius: 8px; line-height: 1.6; color: #e5e7eb; }
    .news-card { border-bottom: 1px solid #1f2937; padding: 10px 0; }
    .stButton>button { background: #00ffaa; color: black; border-radius: 0; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. Client Initialization with Grounding
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Intelligence Logic (Stress-Run AI)
def run_deep_research(query):
    is_ticker = query.startswith("$")
    target = query.replace("$", "").upper()
    
    # Grounding Configuration (Live Web Access)
    google_search_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[google_search_tool],
        temperature=0.2 # Lower temperature for "Stress-Run" precision
    )

    if is_ticker:
        prompt = f"""
        STRESS-RUN ANALYSIS: {target}
        1. MACRO/MICRO: Scour live news and Meta/Social sentiment for {target}. What is the 'real' market consensus?
        2. RESULTS: Analyze the latest quarterly results and management's tone (Hawkish/Dovish).
        3. ASYMMETRIC BETS: Identify the supply chain for {target}. Is there a Tier 2/3 supplier that is a BETTER bet than {target}?
        4. SELF-CRITIQUE: Evaluate the risks of {target} vs these suppliers.
        STRICT: End with 'TICKERS: {target}, [BET_TICKER_1], [BET_TICKER_2]'
        """
    else:
        prompt = f"""
        SUPPLY CHAIN MAPPER: {query}
        1. MAP: Detail the Tier 1, 2, and 3 players for {query}.
        2. BOTTLENECK: Who owns the critical patents or raw materials?
        3. ASYMMETRIC PLAYS: Suggest 3 obscure public companies with massive upside potential.
        STRICT: End with 'TICKERS: [T1], [T2], [T3]'
        """
    
    return client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=config
    )

# 4. Interface Layout
st.title("🏦 ALPHA TERMINAL | AGENTIC v5")
st.caption("Live Grounding Enabled | Supply Chain Intelligence | March 2026")

user_input = st.text_input("RESEARCH TARGET:", placeholder="e.g. 'Solid State Electrolytes' or '$NVDA'")

if st.button("RUN DEEP ALPHA SCAN"):
    with st.spinner("AGENT STRESS-TESTING DATA..."):
        response = run_deep_research(user_input)
        report_body = response.text
        
        # Display Research
        st.markdown("### 🧠 ANALYST INTELLIGENCE")
        st.markdown(f"<div class='report-box'>{report_body.split('TICKERS:')[0]}</div>", unsafe_allow_html=True)
        
        # Extract Tickers
        match = re.search(r'TICKERS:?\s*([\w\s,$.\[\]]+)', report_body, re.IGNORECASE)
        if match:
            tickers = [t.strip().upper().replace('$', '').replace('[','').replace(']','') for t in match.group(1).split(',')]
            
            # --- MARKET DATA TABLE ---
            st.markdown("### 📊 FINANCIAL WORKSTATION")
            financials = []
            for t in tickers:
                try:
                    s = yf.Ticker(t)
                    info = s.info
                    financials.append({
                        "TICKER": t,
                        "COMPANY": info.get('shortName', 'N/A'),
                        "PRICE": f"${info.get('currentPrice', 0):,.2f}",
                        "UPSIDE": f"{((info.get('targetMedianPrice', 0)-info.get('currentPrice', 0))/info.get('currentPrice', 1)*100):+.1f}%",
                        "RATIO (P/E)": info.get('forwardPE', 'N/A'),
                        "MCAP": f"${info.get('marketCap', 0)/1e9:.1f}B"
                    })
                except: continue
            st.table(pd.DataFrame(financials))

            # --- NEWS FEED (THE REQUESTED FEATURE) ---
            st.markdown("### 📰 LIVE INTELLIGENCE FEED")
            n_cols = st.columns(len(tickers))
            for idx, t in enumerate(tickers):
                with n_cols[idx]:
                    st.write(f"**{t} News**")
                    news_items = yf.Search(t, news_count=5).news
                    for n in news_items:
                        st.markdown(f"<div class='news-card'><a href='{n['link']}' style='color:#00ffaa;'>{n['title']}</a><br><small>{n['publisher']}</small></div>", unsafe_allow_html=True)
        else:
            st.warning("Could not identify specific tickers for market data.")

else:
    st.info("Terminal Idle. Input a Ticker (with $) or Sector to engage Research Agent.")

st.divider()
st.caption("INTERNAL USE ONLY - System Grounded via Google Search API")
