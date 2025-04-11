import requests
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh


load_dotenv()
api_key = os.getenv("API_KEY")

# App title and description
st.set_page_config(page_title="Bitcoin Investment Tracker", layout="wide")

st_autorefresh(interval=60000, key="refresh")

st.title("📈 Bitcoin Investment Tracker")
st.markdown("Monitor your BTC investment in real-time with logged data.")

# Load CSV
csv_file = "btc_price_log.csv"

try:
    df = pd.read_csv(csv_file)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Sort by latest timestamp
    df = df.sort_values(by='timestamp', ascending=False)

    # Success message
    st.success("CSV loaded successfully!")

    # Show columns
    with st.expander("📁 CSV Columns:"):
        st.json(list(df.columns))
        st.dataframe(df.head())

    # Latest values
    latest = df.iloc[0]
    current_price = latest['btc_price_inr']
    current_value = latest['value_inr']
    current_profit = latest['profit_percent']

    # Show stat cards
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Current BTC Price (INR)", f"₹{current_price:,.0f}")
    col2.metric("📦 Current Value (INR)", f"₹{current_value:,.2f}")
    col3.metric("📈 Profit %", f"{current_profit:.2f}%", delta=f"{current_profit:.2f}%")

    st.markdown("## 📊 BTC Investment Trend")

    # Line chart with BTC price and investment value
    chart_data = df[['timestamp', 'btc_price_inr', 'value_inr']].set_index('timestamp')
    st.line_chart(chart_data)

    st.markdown("## 📉 Profit Percentage Over Time")

    # Profit bar chart
    profit_data = df[['timestamp', 'profit_percent']].set_index('timestamp')
    st.bar_chart(profit_data)

except Exception as e:
    st.error(f"Error loading CSV: {e}")


def get_news_sentiment():
    url = f"https://newsapi.org/v2/everything?q=bitcoin&apiKey={api_key}&pageSize=5&sortBy=publishedAt"
    response = requests.get(url)
    articles = response.json().get("articles", [])

    sentiment_scores = []
    headlines = []

    for article in articles:
        title = article["title"]
        headlines.append((title, article["url"]))
        if "crash" in title.lower() or "fall" in title.lower():
            sentiment_scores.append(-0.6)
        elif "surge" in title.lower() or "rise" in title.lower():
            sentiment_scores.append(0.5)
        else:
            sentiment_scores.append(0)

    avg_score = round(sum(sentiment_scores) / len(sentiment_scores), 2) if sentiment_scores else 0
    return avg_score, headlines


st.subheader("🧠 News Sentiment Insights")

avg_score, headlines = get_news_sentiment()

st.write(f"**Average Sentiment Score:** `{avg_score}`")

if avg_score < -0.3:
    st.error("🚨 Negative sentiment detected in recent news!")
else:
    st.success("✅ Sentiment looks normal.")

st.markdown("### 📰 Latest News")
for title, link in headlines:
    st.markdown(f"- [{title}]({link})")


