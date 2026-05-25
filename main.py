import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from bot.telegram_bot import TelegramNotifier, load_stocks
from bot.data_fetcher import fetch_intraday_data, get_current_price
from bot.indicators import add_technical_indicators, generate_technical_signal
from bot.ai_predictor import AIPredictor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def analyze_stock(ticker: str, ai_predictors: dict) -> str:
    """
    Fetches data, runs technical + AI analysis, and returns a formatted signal message if applicable.
    """
    logger.info(f"Analyzing {ticker}...")

    # Ensure there is a specific AI predictor for this stock
    if ticker not in ai_predictors:
        ai_predictors[ticker] = AIPredictor()
    ai = ai_predictors[ticker]

    # 1. Fetch Data
    df = fetch_intraday_data(ticker, interval='1h', days_back=60) # Fetch 60 days of hourly data for good indicator/AI context
    if df.empty:
        return ""

    # 2. Add Technical Indicators
    df_with_indicators = add_technical_indicators(df)
    if df_with_indicators.empty:
        return ""

    # 3. Generate Traditional Technical Signal
    tech_signal = generate_technical_signal(df_with_indicators)

    # 4. Generate AI Prediction
    # (The AI trains itself on the provided dataframe if it hasn't been trained yet)
    ai_signal = ai.predict(df_with_indicators)

    # 5. Hybrid Strategy Decision Logic
    final_signal = "HOLD"

    # Strict Buy: Both AI and Technicals must agree
    if tech_signal == "BUY" and ai_signal == "UP":
        final_signal = "BUY"
    # Strict Sell: Both AI and Technicals must agree
    elif tech_signal == "SELL" and ai_signal == "DOWN":
        final_signal = "SELL"
    # Weak Buy: AI predicts UP, but Technicals are neutral (Hold)
    elif tech_signal == "HOLD" and ai_signal == "UP":
        final_signal = "WEAK BUY"
    # Weak Sell: AI predicts DOWN, but Technicals are neutral (Hold)
    elif tech_signal == "HOLD" and ai_signal == "DOWN":
         final_signal = "WEAK SELL"

    # Only notify on strong or weak buy/sell (ignore standard holds)
    if final_signal != "HOLD":
        current_price = get_current_price(ticker)

        # Format the alert
        emoji = "🟢" if "BUY" in final_signal else "🔴"
        message = (
            f"{emoji} *{final_signal} SIGNAL: {ticker}*\n"
            f"Price: ${current_price:.2f}\n"
            f"Tech Indicators: {tech_signal}\n"
            f"AI Prediction: {ai_signal}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        return message

    return ""

async def main_loop():
    """The continuous monitoring loop."""
    logger.info("Initializing bot components...")

    # Initialize Notifier and start command listener
    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    await notifier.start_listening()

    # Dictionary to keep individual trained models for each stock
    ai_predictors = {}

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        await notifier.send_message("🚀 Bot started! Monitoring stocks continuously...")
    else:
        logger.warning("Running without Telegram notifications (Check your .env file).")

    while True:
        try:
            # Simple check if it's weekend, wait
            now = datetime.now()
            if now.weekday() >= 5: # Saturday or Sunday
                logger.info("Market is closed (Weekend). Sleeping for 1 hour...")
                await asyncio.sleep(3600)
                continue

            stocks_to_monitor = load_stocks()
            logger.info(f"Starting analysis cycle for {len(stocks_to_monitor)} stocks...")

            for ticker in stocks_to_monitor:
                signal_message = await analyze_stock(ticker, ai_predictors)

                if signal_message:
                    logger.info(f"Signal triggered for {ticker}")
                    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                        await notifier.send_message(signal_message)

                # Sleep briefly between requests to avoid rate-limiting from Yahoo Finance
                await asyncio.sleep(2)

            logger.info("Analysis cycle complete. Sleeping for 1 hour...")
            # Sleep until top of the next hour
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0)
            if now.hour == 23:
                 next_hour = next_hour.replace(hour=0, day=now.day + 1)
            else:
                 next_hour = next_hour.replace(hour=now.hour + 1)

            sleep_seconds = (next_hour - now).total_seconds()

            # If it's very close to top of hour, sleep until the next one to avoid double-firing
            if sleep_seconds < 60:
                sleep_seconds += 3600

            logger.info(f"Sleeping for {sleep_seconds} seconds until next check...")
            await asyncio.sleep(sleep_seconds)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(60) # Sleep 1 minute on error before retrying

if __name__ == "__main__":
    # Ensure asyncio event loop handles the async execution
    try:
         asyncio.run(main_loop())
    except KeyboardInterrupt:
         logger.info("Bot stopped by user.")
