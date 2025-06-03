def calculate_confidence(data):
    # מוודא שיש מספיק נתונים
    if len(data) < 30:
        return 0

    confidence = 0
    total_indicators = 3

    # ממוצעים נעים
    data['SMA5'] = data['Close'].rolling(window=5).mean()
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    try:
        if pd.notna(data['SMA5'].iloc[-1]) and pd.notna(data['SMA20'].iloc[-1]):
            if data['SMA5'].iloc[-1] > data['SMA20'].iloc[-1]:
                confidence += 1
    except:
        pass

    # RSI
    try:
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        RS = gain / loss
        RSI = 100 - (100 / (1 + RS))
        if pd.notna(RSI.iloc[-1]) and RSI.iloc[-1] < 70:
            confidence += 1
    except:
        pass

    # MACD
    try:
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        if pd.notna(macd.iloc[-1]) and pd.notna(signal.iloc[-1]):
            if macd.iloc[-1] > signal.iloc[-1]:
                confidence += 1
    except:
        pass

    return round((confidence / total_indicators) * 100)
