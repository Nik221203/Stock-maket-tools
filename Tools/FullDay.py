import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import talib

# List of stock symbols
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
    'BIOCON.NS', 'MRF.NS', 'LICHSGFIN.NS', 'CONCOR.NS', 'DLF.NS','BEML.NS', 'BEL.NS', 'HAL.NS', 'MTARTECH.NS', 'SOLARA.NS',
    'LUPIN.NS', 'AUROBINDO.NS', 'GLENMARK.NS', 'ZYDUSLIFE.NS', 'TORNTPHARM.NS', 'ALKEM.NS'
]


# Candlestick pattern detection function
def detect_pattern(open_, high, low, close):
    patterns = {
        'Bearish Engulfing': talib.CDLENGULFING(open_, high, low, close),
        'Hanging Man': talib.CDLHANGINGMAN(open_, high, low, close),
        'Dark Cloud Cover': talib.CDLDARKCLOUDCOVER(open_, high, low, close),
        'Bearish Harami': talib.CDLHARAMI(open_, high, low, close),
        'Bearish Doji Star': talib.CDLDOJISTAR(open_, high, low, close),
        'Bearish Kicking': talib.CDLKICKING(open_, high, low, close),
        'Three Black Crows': talib.CDL3BLACKCROWS(open_, high, low, close),
        'Advance Block': talib.CDLADVANCEBLOCK(open_, high, low, close),
        'Hammer': talib.CDLHAMMER(open_, high, low, close),
        'Doji': talib.CDLDOJI(open_, high, low, close),
        'Bullish Engulfing': talib.CDLENGULFING(open_, high, low, close),
        'Shooting Star': talib.CDLSHOOTINGSTAR(open_, high, low, close),
        'Evening Star': talib.CDLEVENINGSTAR(open_, high, low, close),
        'Morning Star': talib.CDLMORNINGSTAR(open_, high, low, close)
    }
    for name, result in patterns.items():
        # Check last candle for pattern occurrence (non-zero means pattern detected)
        if result[-2] != 0:
            return name
    return "None"


# Main function to get breakout/breakdown signals and patterns
def get_intraday_signals(stocks):
    breakouts = []
    breakdowns = []

    for symbol in stocks:
        try:
            # Download previous 5 days daily data to get previous day's high and low
            df_prev = yf.download(symbol, period="5d", interval="1d")
            if df_prev.empty or len(df_prev) < 2:
                continue

            prev_high = df_prev['High'].iloc[-2].item()
            prev_low = df_prev['Low'].iloc[-2].item()

            # Download today's 5-min interval data
            df_today = yf.download(symbol, period="1d", interval="15m").dropna()
            if df_today.empty or len(df_today) < 10:
                continue

            latest_price = df_today['Close'].iloc[-1].item()
            latest_volume = df_today['Volume'].iloc[-1].item()

            # Convert to 1D numpy arrays for TA-Lib
            o = df_today['Open'].values.astype(np.float64).ravel()
            h = df_today['High'].values.astype(np.float64).ravel()
            l = df_today['Low'].values.astype(np.float64).ravel()
            c = df_today['Close'].values.astype(np.float64).ravel()

            # Detect pattern on the full day data
            pattern = detect_pattern(o, h, l, c)

            # Check breakout/breakdown conditions
            if latest_price > prev_high:
                breakouts.append({
                    'Stock': symbol,
                    'Pattern': pattern,
                    'Prev High': round(prev_high, 2),
                    'Current Price': round(latest_price, 2),
                    'Volume (15-min)': int(latest_volume)
                })
            elif latest_price < prev_low:
                breakdowns.append({
                    'Stock': symbol,
                    'Pattern': pattern,
                    'Prev Low': round(prev_low, 2),
                    'Current Price': round(latest_price, 2),
                    'Volume (15-min)': int(latest_volume)
                })

        except Exception as e:
            st.warning(f"Error processing {symbol}: {e}")

    return breakouts, breakdowns

# Streamlit UI
st.title("Intraday Stock Breakout & Breakdown Scanner with Full-Day Pattern Detection")

breakouts, breakdowns = get_intraday_signals(stock_list)

if breakouts:
    st.subheader("📈 Breakout Stocks")
    df_b = pd.DataFrame(breakouts)
    st.dataframe(df_b)
else:
    st.write("No breakout stocks found.")

if breakdowns:
    st.subheader("📉 Breakdown Stocks")
    df_d = pd.DataFrame(breakdowns)
    st.dataframe(df_d)
else:
    st.write("No breakdown stocks found.")
