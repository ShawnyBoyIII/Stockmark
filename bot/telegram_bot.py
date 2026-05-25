import os
import json
import logging
from typing import List
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

STOCKS_FILE = "stocks.json"

# Default small-cap stocks
DEFAULT_STOCKS = [
    "MSTR", "CELH", "SMCI", "ELF", "RXRX",
    "ALKT", "HIMS", "SOUN", "PLTR", "IONQ"
]

def load_stocks() -> List[str]:
    """Loads stocks from file or creates it with defaults."""
    if not os.path.exists(STOCKS_FILE):
        save_stocks(DEFAULT_STOCKS)
        return DEFAULT_STOCKS
    try:
        with open(STOCKS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading stocks: {e}")
        return DEFAULT_STOCKS

def save_stocks(stocks: List[str]):
    """Saves the current stock list to a file."""
    try:
        with open(STOCKS_FILE, "w") as f:
            json.dump(stocks, f)
    except Exception as e:
        logger.error(f"Error saving stocks: {e}")

def is_authorized(update: Update) -> bool:
    """Checks if the user sending the message is authorized."""
    allowed_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    return allowed_chat_id and str(update.effective_chat.id) == allowed_chat_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    if not is_authorized(update):
        return

    welcome_message = (
        "📈 Welcome to your Stock Market AI Bot!\n\n"
        "I am running and monitoring your stocks continuously.\n"
        "I will message you here if I find a BUY or SELL signal.\n\n"
        "To add a new stock to monitor, type:\n"
        "`/add TICKER` (e.g., `/add AAPL`)\n\n"
        "To view your current list, type `/list`."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, parse_mode='Markdown')

async def add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /add <ticker> command."""
    if not is_authorized(update):
        return

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please provide a ticker symbol. Example: `/add AAPL`",
            parse_mode='Markdown'
        )
        return

    new_ticker = context.args[0].upper()
    current_stocks = load_stocks()

    if new_ticker in current_stocks:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ {new_ticker} is already in your monitoring list."
        )
    else:
        current_stocks.append(new_ticker)
        save_stocks(current_stocks)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Successfully added {new_ticker} to your monitoring list!"
        )

async def list_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /list command."""
    if not is_authorized(update):
        return

    current_stocks = load_stocks()
    stock_list = "\n".join([f"- {s}" for s in current_stocks])
    message = f"📋 *Currently Monitored Stocks:*\n\n{stock_list}"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode='Markdown'
    )

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        if not self.token or not self.chat_id:
            logger.error("Telegram token or Chat ID is missing. Notifications will fail.")
        else:
            self.app = ApplicationBuilder().token(self.token).build()
            # Register commands
            self.app.add_handler(CommandHandler("start", start))
            self.app.add_handler(CommandHandler("add", add_stock))
            self.app.add_handler(CommandHandler("list", list_stocks))

    async def start_listening(self):
        """Starts the bot to listen for commands in the background."""
        if self.app:
             logger.info("Starting Telegram bot listener...")
             await self.app.initialize()
             await self.app.start()
             await self.app.updater.start_polling()

    async def send_message(self, text: str):
        """Sends a message to the specified chat ID."""
        if not self.app or not self.chat_id:
            logger.warning("Cannot send message: App not initialized or Chat ID missing.")
            return

        try:
            await self.app.bot.send_message(chat_id=self.chat_id, text=text, parse_mode='Markdown')
            logger.info(f"Telegram message sent: {text[:30]}...")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
