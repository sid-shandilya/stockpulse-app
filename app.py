import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(
    page_title="StockPulse Super App", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# !!! PASTE YOUR KEY HERE !!!
api_key = "AIzaSyCYdqSca3--0MkYlXIgsDZQLC09Pft4fiY" 

# --- HELPER: SMART MODEL DETECTOR ---
def get_working_model(api_key):
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    return m.name
    except:
        pass
    return "gemini-pro"

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        try:
            news = stock.news
        except:
            news = []
        try:
            insider = stock.insider_transactions
        except:
            insider = pd.DataFrame()
        return hist, news, stock.info, insider
    except:
        return None, None, None, None

def analyze_sentiment(news_list, api_key, eli5_mode=False):
    if "PASTE" in api_key: return "⚠️ Add API Key!", 0
    if not news_list: return "No news found.", 0

    model_name = get_working_model(api_key)
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        return f"Model Error: {e}", 0
    
    headlines = []
    for n in news_list[:5]:
        title = n.get('title', n.get('content', {}).get('title', ''))
        if title: headlines.append(title)
            
    if not headlines: return "No headlines.", 0
    
    tone = "Explain simply like I'm 5. Use emojis." if eli5_mode else "Use professional tone."
    prompt = f"Analyze sentiment for: {headlines}. {tone} Return strictly: SCORE: [Float -1.0 to 1.0] SUMMARY: [2-sentence summary]"
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "SCORE" not in text: return f"{text[:100]}...", 0
        score = float(text.split("SCORE:")[1].split("\n")[0].strip())
        summary = text.split("SUMMARY:")[1].strip()
        return summary, score
    except Exception as e:
        return f"Analysis Failed: {str(e)}", 0

# --- MAIN UI ---
st.header("📈 StockPulse")

# 1. QUICK SELECT
col_q1, col_q2, col_q3, col_q4 = st.columns(4)
if 'selected_ticker' not in st.session_state: st.session_state.selected_ticker = "GOOGL"

def set_ticker(t): st.session_state.selected_ticker = t
if col_q1.button("NVDA"): set_ticker("NVDA")
if col_q2.button("TSLA"): set_ticker("TSLA")
if col_q3.button("AAPL"): set_ticker("AAPL")
if col_q4.button("BTC-USD"): set_ticker("BTC-USD")

ticker_input = st.text_input("Ticker:", value=st.session_state.selected_ticker).upper()

if ticker_input:
    with st.spinner("Crunching numbers..."):
        hist, news, info, insider = get_stock_data(ticker_input)
        
        if hist is None or hist.empty:
            st.error("Stock not found.")
        else:
            current_price = hist['Close'].iloc[-1]
            
            # --- TABS ---
            tab1, tab2, tab3 = st.tabs(["📊 Price", "🤖 AI & News", "🕵️ Insider & Fun"])
            
            with tab1:
                m1, m2, m3 = st.columns(3)
                delta = ((current_price - hist['Close'].iloc[-2])/hist['Close'].iloc[-2])*100 if len(hist) > 1 else 0
                m1.metric("Price", f"${current_price:.2f}", f"{delta:.2f}%")
                m2.metric("High (1y)", f"${hist['High'].max():.2f}")
                m3.metric("Low (1y)", f"${hist['Low'].min():.2f}")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], fill='tozeroy', line_color='#00CC96'))
                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                col_ai_head, col_ai_tog = st.columns([3,1])
                col_ai_head.subheader("Sentiment Analysis")
                eli5 = col_ai_tog.toggle("Explain like I'm 5 👶", value=False)
                
                summary, score = analyze_sentiment(news, api_key, eli5)
                
                if isinstance(score, float) and score != 0:
                    st.progress((score + 1) / 2)
                    if score > 0.2: st.success(summary)
                    elif score < -0.2: st.error(summary)
                    else: st.info(summary)
                else:
                    st.warning(summary)

                st.divider()
                st.caption("Latest News (Opens in New Tab)")
                
                # --- THE FIX: Force New Tab with HTML ---
                for n in news[:5]:
                    title = n.get('title', 'Read Article')
                    link = n.get('link')
                    
                    # Only render if we have a valid link
                    if link and link.startswith('http'):
                        # HTML anchor tag with target="_blank"
                        st.markdown(
                            f'<a href="{link}" target="_blank" style="text-decoration: none; color: #00CC96; font-weight: bold;">🔗 {title}</a>', 
                            unsafe_allow_html=True
                        )
                        st.write("") # Spacer

            with tab3:
                st.subheader("⏳ Time Machine")
                if not hist.empty:
                    start_price_1y = hist['Close'].iloc[0]
                    roi = ((current_price - start_price_1y) / start_price_1y) * 100
                    final_value = 1000 * (1 + roi/100)
                    color = "green" if roi > 0 else "red"
                    st.markdown(f"If you invested $1,000 exactly 1 year ago, you'd have: :{color}[${final_value:,.2f}]")
                
                st.divider()
                st.subheader("🕵️ Insider Moves")
                if insider is not None and not insider.empty:
                    insider_clean = insider.copy()
                    # Safe Date logic...
                    date_col = None
                    for col in ['Start Date', 'Date', 'Transaction Date']:
                        if col in insider_clean.columns:
                            date_col = col
                            break
                    if date_col:
                        try:
                            insider_clean[date_col] = pd.to_datetime(insider_clean[date_col])
                            insider_clean.set_index(date_col, inplace=True)
                            insider_clean.index = insider_clean.index.date
                        except: pass
                    
                    cols = [c for c in ['Text', 'Shares', 'Value'] if c in insider_clean.columns]
                    st.dataframe(insider_clean[cols].head(5) if cols else insider_clean.head(5), use_container_width=True)
                else:
                    st.info("No insider data available.")
