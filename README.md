# Stock Market AI & Technical Analysis Bot

This bot continuously monitors a list of stocks throughout the trading day, combining traditional mathematical indicators (RSI, MACD, Moving Averages) with AI predictions (Machine Learning) to send Buy, Sell, or Hold signals directly to you via Telegram.

## Features
- **Intraday Monitoring:** Checks stock prices and indicators hourly.
- **Hybrid Strategy:** Uses `yfinance` to fetch data, calculates standard technical indicators (using the `ta` library), and uses a `scikit-learn` Random Forest model to predict short-term price movement.
- **Telegram Integration:** Sends signals directly to your phone/desktop via Telegram.
- **Interactive:** You can add new stocks for the bot to monitor by messaging it directly on Telegram.

---

## Setup Instructions

### 1. Create a Telegram Bot & Get Your Token
1. Open the Telegram app and search for **BotFather** (it has a verified checkmark).
2. Start a chat with BotFather and send the command `/newbot`.
3. Follow the prompts to give your bot a name and a username (must end in `bot`).
4. BotFather will give you an HTTP API Token (it looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`). **Save this token.**

### 2. Get Your Telegram Chat ID
1. Search for **userinfobot** (or similar bots like IDBot) in Telegram.
2. Start a chat and send `/start`.
3. The bot will reply with your `Id` (a string of numbers like `987654321`). **Save this ID.**

### 3. Set Up Your Environment
1. In the root of this project, create a file named `.env`.
2. Open `.env` and add your Token and Chat ID like this:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 4. Install Dependencies
Run the following command in your terminal to install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 5. Run the Bot
Start the bot by running:
```bash
python main.py
```

## How to Use
- The bot will start monitoring a default list of 10 small-cap stocks.
- It will send you a message when a Buy or Sell signal is triggered based on the hybrid strategy.
- **To add a stock:** Send a message to your bot on Telegram formatted like this: `/add TICKER` (e.g., `/add AAPL`).
