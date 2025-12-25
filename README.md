# 📈 StockPulse: AI Sentiment Analyzer

StockPulse is a real-time financial dashboard that democratizes stock analysis. It combines live market data with Generative AI to provide instant sentiment analysis of financial news, helping retail investors understand market mood without reading lengthy reports.

## 🚀 Live Demo
[**Click here to view the Live App**](YOUR_STREAMLIT_LINK_HERE)

## ✨ Key Features
* **Real-Time Data:** Fetches live stock prices and 30-day historical data using `yfinance`.
* **AI Sentiment Analysis:** Uses **Google Gemini Pro** to analyze the latest news headlines and generate a sentiment score (Bullish/Bearish) + executive summary.
* **Interactive Charts:** Visualizes price trends using Plotly.
* **Robust Error Handling:** Auto-detects available AI models and handles missing data gracefully.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **AI/LLM:** Google Gemini API (gemini-pro / gemini-1.5-flash)
* **Data Source:** Yahoo Finance API (`yfinance`)
* **Visualization:** Plotly
* **Language:** Python 3.10+

## ⚙️ How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/stockpulse-app.git](https://github.com/YOUR_USERNAME/stockpulse-app.git)
    cd stockpulse-app
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API Keys**
    * Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    * Create a `.streamlit/secrets.toml` file (or just input it in the app sidebar if configured).

4.  **Run the app**
    ```bash
    streamlit run app.py
    ```

## 📄 License
This project is open-source and available under the MIT License.
