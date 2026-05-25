import pandas as pd
import ta

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame with OHLCV data and adds technical indicators.
    """
    if df.empty or len(df) < 30: # Need enough data to calculate indicators
        return df

    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # 1. Moving Averages
    # Simple Moving Average (SMA) - 20 period
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    # Exponential Moving Average (EMA) - 50 period
    df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)

    # 2. Relative Strength Index (RSI) - 14 period
    df['RSI_14'] = ta.momentum.rsi(df['Close'], window=14)

    # 3. Moving Average Convergence Divergence (MACD)
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Diff'] = macd.macd_diff() # Histogram

    # 4. Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_High'] = bollinger.bollinger_hband()
    df['BB_Low'] = bollinger.bollinger_lband()
    df['BB_Mid'] = bollinger.bollinger_mavg()

    # Drop NA values created by rolling windows (e.g., first 50 rows for EMA_50)
    df = df.dropna()

    return df

def generate_technical_signal(df: pd.DataFrame) -> str:
    """
    Evaluates the latest indicators to generate a basic technical Buy/Sell/Hold signal.
    This serves as the 'traditional mathematical' part of the hybrid strategy.
    """
    if df.empty or len(df) < 1:
        return 'HOLD'

    latest = df.iloc[-1]

    rsi = latest['RSI_14']
    macd_diff = latest['MACD_Diff']
    close_price = latest['Close']
    sma_20 = latest['SMA_20']

    # Simple logic
    buy_signals = 0
    sell_signals = 0

    # RSI Logic
    if rsi < 30: # Oversold
        buy_signals += 1
    elif rsi > 70: # Overbought
        sell_signals += 1

    # MACD Logic
    if macd_diff > 0: # Bullish momentum
        buy_signals += 1
    elif macd_diff < 0: # Bearish momentum
        sell_signals += 1

    # Price vs SMA
    if close_price > sma_20: # Uptrend
        buy_signals += 1
    elif close_price < sma_20: # Downtrend
        sell_signals += 1

    if buy_signals >= 2 and sell_signals == 0:
        return 'BUY'
    elif sell_signals >= 2 and buy_signals == 0:
        return 'SELL'
    else:
        return 'HOLD'
