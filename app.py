%%writefile app.py
import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="StockPulse AI", layout="wide")

# !!! PASTE YOUR KEY HERE !!!
api_key = "AIzaSyCYdqSca3--0MkYlXIgsDZQLC09Pft4fiY" 

# --- HELPER: AUTO-DETECT MODEL ---
def get_working_model(api_key):
    """Automatically finds a model that works for your API Key"""
    genai.configure(api_key=api_key)
    
    # 1. Try to list models your key can access
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    # Found a valid Gemini model! Return its name.
                    print(f"Using Model: {m.name}")
                    return m.name
    except Exception as e:
        print(f"List models failed: {e}")
    
    # 2. Fallback list if auto-detect fails
    return "gemini-1.5-flash"

# --- FUNCTIONS ---
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        # safely try to get news, return empty list if it fails
        try:
            news = stock.news
        except:
            news = []
        return hist, news, stock.info
    except Exception as e:
        return None, None, None

def analyze_sentiment(news_list, api_key):
    if "PASTE" in api_key:
        return "⚠️ You need to paste your actual API Key in the code first!", 0
    
    if not news_list:
        return "No recent news found to analyze.", 0

    # Auto-detect the best model name
    model_name = get_working_model(api_key)
    
    try:
        model = genai.GenerativeModel(model_name)
    except:
        return f"Error: Could not load model '{model_name}'. Check API Key.", 0
    
    # --- ROBUST TITLE EXTRACTION ---
    headlines = []
    for n in news_list[:5]:
        if 'title' in n:
            headlines.append(n['title'])
        elif 'content' in n and 'title' in n['content']:
            headlines.append(n['content']['title'])
        else:
            continue
            
    if not headlines:
        return "Could not extract readable headlines from Yahoo Finance.", 0
    
    prompt = f"""
    Act as a Wall Street Financial Analyst. Analyze the sentiment of these 5 headlines for a single stock:
    {headlines}
    
    Output strictly in this format:
    SENTIMENT_SCORE: [A number between -1.0 (Very Negative) and 1.0 (Very Positive)]
    SUMMARY: [A 2-sentence summary of the key risks or opportunities mentioned]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Safety check for response format
        if "SENTIMENT_SCORE" not in text:
            return f"AI Analysis: {text}", 0
            
        score_line = [line for line in text.split('\n') if "SENTIMENT_SCORE" in line][0]
        score = float(score_line.split(":")[1].strip())
        summary_line = text.split("SUMMARY:")[1].strip()
        return summary_line, score
    except Exception as e:
        return f"Error parsing AI response: {e}", 0

# --- MAIN UI ---
st.title("📈 StockPulse: AI Sentiment Analyzer")
col1, col2 = st.columns([1, 2])

with col1:
    ticker = st.text_input("Stock Ticker", value="GOOGL").upper()
    if st.button("Analyze Stock"):
        with st.spinner(f"Fetching data for {ticker}..."):
            hist, news, info = get_stock_data(ticker)
            if hist is None or hist.empty:
                st.error("Invalid Ticker or No Data Found.")
            else:
                current_price = hist['Close'].iloc[-1]
                st.metric("Current Price", f"${current_price:.2f}")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Price'))
                fig.update_layout(title="30-Day Trend", height=300, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'hist' in locals() and hist is not None and not hist.empty:
        st.subheader(f"🤖 AI Sentiment Analysis ({ticker})")
        with st.spinner("Consulting Gemini AI..."):
            summary, score = analyze_sentiment(news, api_key)
        
        # Display results only if valid score returned
        if isinstance(score, (int, float)):
            if score > 0.3:
                color = "green"
                mood = "Bullish 🐂"
            elif score < -0.3:
                color = "red"
                mood = "Bearish 🐻"
            else:
                color = "gray"
                mood = "Neutral 😐"
                
            st.markdown(f"### Sentiment: :{color}[{mood}]")
            st.progress((score + 1) / 2)
            st.info(f"**Analyst Summary:** {summary}")
        else:
            st.warning(summary)
