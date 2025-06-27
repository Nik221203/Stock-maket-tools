import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import talib

# Stocks list
stock_list = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
    'SBIN.NS', 'COLPAL.NS', 'LTF.NS', 'HINDUNILVR.NS', 'ITC.NS',
    'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS', 'AXISBANK.NS',
    'LT.NS', 'HDFC.NS', 'MARUTI.NS', 'BAJFINANCE.NS', 'POWERGRID.NS',
    'TECHM.NS', 'NESTLEIND.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'JSWSTEEL.NS',
    'TATASTEEL.NS', 'WIPRO.NS', 'DRREDDY.NS', 'ADANIGREEN.NS', 'HCLTECH.NS',
    'ONGC.NS', 'BPCL.NS', 'GRASIM.NS', 'EICHERMOT.NS', 'DIVISLAB.NS',
    'M&M.NS', 'CIPLA.NS', 'HEROMOTOCO.NS', 'TATAMOTORS.NS', 'BAJAJFINSV.NS',
    'SUNPHARMA.NS', 'SHREECEM.NS', 'INDUSINDBK.NS', 'ICICIPRULI.NS', 'VEDL.NS',
    'GAIL.NS', 'ADANIPORTS.NS', 'DLF.NS', 'BRITANNIA.NS', 'ZEEL.NS',
    'HAVELLS.NS', 'IDFCFIRSTB.NS', 'TATAELXSI.NS', 'L&TFH.NS', 'MUTHOOTFIN.NS',
    'BANKBARODA.NS', 'SRF.NS', 'CROMPTON.NS', 'PETRONET.NS', 'BOSCHLTD.NS',
    'BANDHANBNK.NS', 'AUROPHARMA.NS', 'AMBUJACEM.NS', 'PEL.NS', 'ICICIGI.NS',
    'BIOCON.NS', 'MRF.NS', 'LICHSGFIN.NS', 'CONCOR.NS', 'BEML.NS', 'BEL.NS', 'HAL.NS', 'MTARTECH.NS',
    'SOLARA.NS', 'LUPIN.NS', 'AUROBINDO.NS', 'GLENMARK.NS', 'ZYDUSLIFE.NS',
    'TORNTPHARM.NS', 'ALKEM.NS'
]

# Detect candlestick pattern
def detect_pattern(open_, high, low, close):
    patterns = {
        'Bearish Engulfing': talib.CDLENGULFING(open_, high, low, close),
        'Hanging Man': talib.CDLHANGINGMAN(open_, high, low, close),
        'Dark Cloud Cover': talib.CDLDARKCLOUDCOVER(open_, high, low, close),
        'Bearish Harami': talib.CDLHARAMI(open_, high, low, close),
        'Doji': talib.CDLDOJI(open_, high, low, close),
        'Bullish Engulfing': talib.CDLENGULFING(open_, high, low, close),
        'Shooting Star': talib.CDLSHOOTINGSTAR(open_, high, low, close),
        'Evening Star': talib.CDLEVENINGSTAR(open_, high, low, close),
        'Morning Star': talib.CDLMORNINGSTAR(open_, high, low, close),
        'Hammer': talib.CDLHAMMER(open_, high, low, close)
    }
    for name, result in patterns.items():
        if result[-2] != 0:
            return name
    return "None"

# Prediction logic
def get_prediction(latest_price, prev_high, prev_low, pattern, rsi, macd, macdsignal, ema20, ema50):
    trend = "Uptrend" if ema20[-1] > ema50[-1] else "Downtrend"
    rsi_signal = "Overbought" if rsi[-1] > 70 else ("Oversold" if rsi[-1] < 30 else "Neutral")
    macd_signal = "MACD Bullish" if macd[-1] > macdsignal[-1] else "MACD Bearish"

    if latest_price > prev_high:
        if "Bearish" in pattern or "Shooting" in pattern or rsi_signal == "Overbought":
            return "⚠️ Breakout - Weak/Bearish"
        elif macd_signal == "MACD Bullish" and trend == "Uptrend":
            return "✅ Breakout - Strong Bullish"
        else:
            return "📈 Breakout - Bullish"
    elif latest_price < prev_low:
        if "Bullish" in pattern or rsi_signal == "Oversold":
            return "🔁 Breakdown - Possible Reversal"
        elif macd_signal == "MACD Bearish" and trend == "Downtrend":
            return "📉 Breakdown - Bearish Trend"
        else:
            return "📉 Breakdown"
    else:
        return "⏸ Neutral"

# Main scanner
def get_intraday_signals(stocks):
    breakouts, breakdowns = [], []

    for symbol in stocks:
        try:
            df_daily = yf.download(symbol, period="5d", interval="1d")
            if df_daily.empty or len(df_daily) < 2:
                continue

            prev_high = df_daily['High'].iloc[-2].item()
            prev_low = df_daily['Low'].iloc[-2].item()

            df_intraday = yf.download(symbol, period="1d", interval="15m").dropna()
            if df_intraday.empty or len(df_intraday) < 20:
                continue

            latest_price = df_intraday['Close'].iloc[-1].item()
            latest_vol = int(df_intraday['Volume'].iloc[-1].item())

            o = df_intraday['Open'].values.astype(np.float64).ravel()
            h = df_intraday['High'].values.astype(np.float64).ravel()
            l = df_intraday['Low'].values.astype(np.float64).ravel()
            c = df_intraday['Close'].values.astype(np.float64).ravel()

            # Indicators
            rsi = talib.RSI(c, timeperiod=14)
            macd, macdsignal, _ = talib.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)
            ema20 = talib.EMA(c, timeperiod=20)
            ema50 = talib.EMA(c, timeperiod=50)

            pattern = detect_pattern(o, h, l, c)
            prediction = get_prediction(latest_price, prev_high, prev_low, pattern, rsi, macd, macdsignal, ema20, ema50)

            stock_data = {
                'Stock': symbol,
                'Pattern': pattern,
                'Prev High' if latest_price > prev_high else 'Prev Low': round(prev_high if latest_price > prev_high else prev_low, 2),
                'Current Price': round(latest_price, 2),
                'Volume (15m)': latest_vol,
                'Prediction': prediction
            }

            if latest_price > prev_high:
                breakouts.append(stock_data)
            elif latest_price < prev_low:
                breakdowns.append(stock_data)

        except Exception as e:
            st.error(f"❌ Error processing {symbol}: {e}")

    return breakouts, breakdowns

# Streamlit UI
st.set_page_config(page_title="📊 Stock Signal Scanner", layout="wide")
st.title("📈 Intraday Stock Breakout & Breakdown Scanner (with Prediction)")

with st.spinner("🔍 Scanning market, please wait..."):
    breakouts, breakdowns = get_intraday_signals(stock_list)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Breakout Stocks")
    if breakouts:
        df_break = pd.DataFrame(breakouts)
        st.dataframe(df_break)
    else:
        st.info("No breakout stocks found.")

with col2:
    st.subheader("📉 Breakdown Stocks")
    if breakdowns:
        df_break = pd.DataFrame(breakdowns)
        st.dataframe(df_break)
    else:
        st.info("No breakdown stocks found.")
