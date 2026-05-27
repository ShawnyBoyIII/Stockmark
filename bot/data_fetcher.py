import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def fetch_intraday_data(ticker_symbol: str, interval: str = '1h', days_back: int = 30) -> pd.DataFrame:
    """
    Fetches intraday historical stock data.
    Note: yfinance restricts '1h' data to a maximum of 730 days.
    """
    try:
        # Calculate the start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Download data
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            logger.warning(f"No data found for {ticker_symbol} with interval {interval}.")
            return df

        # Ensure we only keep useful columns and drop any completely missing rows
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.dropna()
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame()

def get_current_price(ticker_symbol: str) -> float:
    """
    Fetches the latest available price for a ticker.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
        return 0.0
    except Exception as e:
        logger.error(f"Error fetching current price for {ticker_symbol}: {e}")
        return 0.0
