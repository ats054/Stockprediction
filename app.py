import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calculate_confidence(data):
    if len(data) < 30:
        return 0

    confidence = 0
    total_indicators = 3

    # SMA
    try:
        data['SMA5'] = data['Close'].rolling(window=5).mean()
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        sma5 = data['SMA5'].iloc[-1]
        sma20 = data['SMA20'].iloc[-1]
        sma5 = sma5.item() if hasattr(sma5, 'item') else sma5
        sma20 = sma20.item() if hasattr(sma20, 'item') else sma20
        if pd.notna(sma5) and pd.notna(sma20) and float(sma5) > float(sma20):
            confidence += 1
    except Exception as e:
        print("SMA error:", e)

    # RSI
    try:
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        RS = gain / loss
        RSI = 100 - (100 / (1 + RS))
        rsi_value = RSI.iloc[-1]
        rsi_value = rsi_value.item() if hasattr(rsi_value, 'item') else rsi_value
        if pd.notna(rsi_value) and float(rsi_value) < 70:
            confidence += 1
    except Exception as e:
        print("RSI error:", e)

    # MACD
    try:
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_val = macd.iloc[-1]
        signal_val = signal.iloc[-1]
        macd_val = macd_val.item() if hasattr(macd_val, 'item') else macd_val
        signal_val = signal_val.item() if hasattr(signal_val, 'item') else signal_val
        if pd.notna(macd_val) and pd.notna(signal_val) and float(macd_val) > float(signal_val):
            confidence += 1
    except Exception as e:
        print("MACD error:", e)

    return round((confidence / total_indicators) * 100)

def predict_next_price(data):
    data = data.reset_index()
    data['Timestamp'] = pd.to_datetime(data['Datetime']).astype(int) / 10**9
    X = data[['Timestamp']]
    y = data['Close']
    model = LinearRegression().fit(X, y)
    next_timestamp = data['Timestamp'].iloc[-1] + (data['Timestamp'].iloc[-1] - data['Timestamp'].iloc[-2])
    predicted_price = model.predict([[next_timestamp]])[0]
    return predicted_price

stocks = {
    '× ××¡×"×§ (NASDAQ)': '^IXIC',
    'S&P 500': '^GSPC',
    '××× (Gold)': 'GC=F',
    '× ××¡×"×§ 100 (NDX)': '^NDX',
    '×ª"× 35': 'TA35.TA',
    'Nvidia': 'NVDA',
    '××××§××× (Bitcoin)': 'BTC-USD',
    "××ª'×¨××× (Ethereum)": 'ETH-USD'
}

intervals = {
    '1 ××§×': '1m',
    '5 ××§××ª': '5m',
    '10 ××§××ª': '15m',
    '30 ××§××ª': '30m',
    '×©×¢×': '60m',
    '×××': '1d',
    '×©×××¢': '1wk'
}

st.set_page_config(page_title="××××× ××¢×ª×× - ×××, ×× ×××ª ××§×¨××¤××", layout="centered")
st.title("ð ×ª××××ª ×××× ×¢× ××××× ×¢×ª×××")
st.write("×××¨ × ××¡, ×××× ××× ××¡××× ××©×§×¢× - ××ª×§×× ×ª××××ª ×¢× ××××× ×××××¨ ××¢×× ××¦× ×©×¢×.")

selected_stock = st.selectbox("×××¨ × ××¡", list(stocks.keys()))
selected_interval_label = st.selectbox("×××¨ ×××× ×××", list(intervals.keys()))
amount = st.number_input("×¡××× ××©×§×¢× ($)", min_value=1, value=1000)

if st.button("×§×× ×ª××××ª"):
    try:
        symbol = stocks[selected_stock]
        interval = intervals[selected_interval_label]
        data = yf.download(symbol, period='5d', interval=interval)

        if data.empty or len(data) < 30:
            raise ValueError("××× ××¡×¤××§ × ×ª×× ×× ××××××")

        data = data.rename_axis("Datetime").reset_index()
        current_price = data['Close'].iloc[-1]
        predicted_price = predict_next_price(data)
        change = predicted_price - current_price
        change_pct = (change / current_price) * 100

        confidence = calculate_confidence(data.set_index("Datetime"))
        recommendation = "×§× ××× ð¼" if confidence >= 66 else "××××× ×¢ â" if confidence < 50 else "××××¨× ð½"
        expected_return = amount * (1 + (confidence - 50)/100)
        profit = expected_return - amount

        st.success(f"×ª××××ª ×-{selected_stock} ××××× {selected_interval_label}: {recommendation}")
        st.info(f"×¡××× ××©×§×¢×: ${amount} | ×¨×××/××¤×¡× ×¦×¤××: ${profit:.2f}")
        st.warning(f"×¨××ª ×××××× ××ª××××ª: {confidence}%")
        st.markdown(f"ð **×××××¨ ×× ××××**: ${current_price:.2f}")
        st.markdown(f"ð® **××××× ×××××¨ ××¢×× ××¦× ×©×¢×**: ${predicted_price:.2f} ({change_pct:.2f}%)")

    except Exception as e:
        st.error(f"×××¨×¢× ×©××××: {e}")
