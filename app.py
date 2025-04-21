import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 📦 Load fallback sample data (since market is closed)
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
df = df[['Date', 'AAPL.Open', 'AAPL.High', 'AAPL.Low', 'AAPL.Close']]
df.columns = ['Date', 'Open', 'High', 'Low', 'Close']
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# 🧠 Custom Pattern Detection

def detect_patterns(df):
    df["Pattern"] = "None"
    for i in range(2, len(df)):
        o, h, l, c = df.iloc[i][['Open', 'High', 'Low', 'Close']]
        body = abs(c - o)
        lower_wick = min(o, c) - l
        upper_wick = h - max(o, c)

        # Hammer
        if body < (h - l) * 0.3 and lower_wick > 2 * body and upper_wick < body:
            df.at[df.index[i], "Pattern"] = "Hammer"

        # Doji
        if abs(o - c) < 0.1 * (h - l):
            df.at[df.index[i], "Pattern"] = "Doji"

        # Bullish Engulfing
        prev_o, prev_c = df.iloc[i - 1][['Open', 'Close']]
        if prev_c < prev_o and c > o and c > prev_o and o < prev_c:
            df.at[df.index[i], "Pattern"] = "Bullish Engulfing"

        # Morning Star (3-candle pattern)
        o2, c2 = df.iloc[i - 2][['Open', 'Close']]
        o1, c1 = df.iloc[i - 1][['Open', 'Close']]
        if (o2 > c2 and
            abs(o1 - c1) < 0.3 * (df.iloc[i - 1]['High'] - df.iloc[i - 1]['Low']) and
            c > o and c > ((o2 + c2) / 2)):
            df.at[df.index[i], "Pattern"] = "Morning Star"

    return df

# 🎨 Streamlit App
st.set_page_config(layout="wide")
st.sidebar.title("📈 Real-time Pattern Scanner (Demo Mode)")
st.title("🧠 Demo Chart — Candlestick Pattern Detection")
st.caption("Market is closed. Showing Apple sample chart with detected patterns: Hammer, Doji, Engulfing, Morning Star")

# 🛠 Detect Patterns
df = detect_patterns(df)

# 📊 Plot Candlestick Chart
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name="Candles"
)])

# 🔍 Add pattern markers
for i in range(len(df)):
    if df['Pattern'].iloc[i] != "None":
        fig.add_trace(go.Scatter(
            x=[df.index[i]],
            y=[df['High'].iloc[i] + 2],
            mode="text",
            text=[df['Pattern'].iloc[i]],
            textposition="top center",
            marker=dict(color="red"),
            name="Pattern"
        ))

fig.update_layout(
    height=700,
    margin=dict(l=40, r=40, t=40, b=40),
    xaxis_rangeslider_visible=False,
    title="Candlestick Chart with Pattern Overlay (Hammer, Doji, Engulfing, Morning Star)"
)

st.plotly_chart(fig, use_container_width=True)