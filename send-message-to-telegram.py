# send-message-to-telegram.py
# by www.ShellHacks.com
pip install yfinance
import requests
import datetime
import yfinance as yf
import os  # Import the os module for environment variables
from telegram import Bot  # Import the Telegram Bot library



def send_telegram_alert(message, alert_type):
    """
    Sends a Telegram alert message.

    Args:
        message (str): The message to send.
        alert_type (str):  "rise" or "fall" (for consistency, though not used)
    """
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if telegram_bot_token and telegram_chat_id:
        try:
            bot = Bot(token=telegram_bot_token)
            bot.send_message(chat_id=telegram_chat_id, text=message)
            print(f"Telegram alert sent ({alert_type}): {message}")  # Improved logging
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")  # Use logging
    else:
        print(
            "Telegram alert not sent.  Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. Message was: %s"
            % message,
        )



def check_nifty_alerts():
    """
    Fetches Nifty data, checks for alerts (MA crossovers, proximity to 52-week extremes),
    and sends Telegram notifications.
    """
    nifty_symbol = "^NSEI"  # Corrected variable name for clarity


    try:
        ticker = yf.Ticker(nifty_symbol)


        history = ticker.history(period="1y")  # Get 1 year of historical data

        if history.empty:
            print("Error: No historical data received from yfinance.")
            return  # Stop processing if no data

        # Get current and previous day's high/low
        low = round(history['Low'].iloc[-1], 2)
        high = round(history['High'].iloc[-1], 2)
        prev_low = round(history['Low'].iloc[-2], 2)
        prev_high = round(history['High'].iloc[-2], 2)

        # Calculate moving averages
        ma_50_list = history['Close'].rolling(window=50).mean()
        ma_50 = round(ma_50_list.iloc[-1], 2)
        prev_ma_50 = round(ma_50_list.iloc[-2], 2)
        ma_100_list = history['Close'].rolling(window=100).mean()
        ma_100 = round(ma_100_list.iloc[-1], 2)
        prev_ma_100 = round(ma_100_list.iloc[-2], 2) # Changed from ma_ma_100_list to ma_100_list
        ma_200_list = history['Close'].rolling(window=200).mean()
        ma_200 = round(ma_200_list.iloc[-1], 2)
        prev_ma_200 = round(ma_200_list.iloc[-2], 2)

        # Logging
        print(f"Current Nifty Price: Low={low}, High={high}")
        print(f"50-day MA: {ma_50}, Previous: {prev_ma_50}")
        print(f"100-day MA: {ma_100}, Previous: {prev_ma_100}")
        print(f"200-day MA: {ma_200}, Previous: {prev_ma_200}")

        # Check for alerts
        nifty_cross_alert(
            prev_low, prev_high, low, high, prev_ma_50, prev_ma_100, prev_ma_200, ma_50, ma_100, ma_200
        )
        is_close_to_52_week_low(low, ticker) # Pass Ticker object
        is_close_to_52_week_high(high, ticker) # Pass Ticker object

    except Exception as e:
        print(f"Error in check_nifty_alerts: {e}")  # Handle errors robustly



def nifty_cross_alert(
    prev_low, prev_high, low, high, prev_ma_50, prev_ma_100, prev_ma_200, ma_50, ma_100, ma_200
):
    """
    Checks for Nifty moving average crossovers and sends alerts.

    Args:
        prev_low (float): Previous day's low.
        prev_high (float): Previous day's high.
        low (float): Current day's low.
        high (float): Current day's high.
        prev_ma_50 (float): Previous day's 50-day moving average.
        prev_ma_100 (float): Previous day's 100-day moving average.
        prev_ma_200 (float): Previous day's 200-day moving average.
        ma_50 (float): Current day's 50-day moving average.
        ma_100 (float): Current day's 100-day moving average.
        ma_200 (float): Current day's 200-day moving average.
    """
    # Check 50 MA crossover
    if (prev_high >= prev_ma_50) and (low <= ma_50):
        send_telegram_alert("Nifty has crossed 50 MA from above", "fall")
    elif (prev_low <= prev_ma_50) and (high >= ma_50):
        send_telegram_alert("Nifty has crossed 50 MA from below", "rise")

    # Check 100 MA crossover
    if (prev_high >= prev_ma_100) and (low <= ma_100):
        send_telegram_alert("Nifty has crossed 100 MA from above", "fall")
    elif (prev_low <= prev_ma_100) and (high >= ma_100):
        send_telegram_alert("Nifty has crossed 100 MA from below", "rise")

    # Check 200 MA crossover
    if (prev_high >= prev_ma_200) and (low <= ma_200):
        send_telegram_alert("Nifty has crossed 200 MA from above", "fall")
    elif (prev_low <= prev_ma_200) and (high >= ma_200):
        send_telegram_alert("Nifty has crossed 200 MA from below", "rise")



def is_close_to_52_week_low(low, ticker): # Changed to accept ticker
    """
    Checks if the current low is within 10% of the 52-week low and sends an alert.

    Args:
        low (float): The current day's low.
        ticker (yf.Ticker): The yfinance Ticker object.
    """
    try:
        fifty_two_week_low = ticker.info['fiftyTwoWeekLow']
        percentage_difference = fifty_two_week_low + fifty_two_week_low * 0.10  # Corrected percentage calculation
        if low <= percentage_difference:
            send_telegram_alert("Nifty is within 10% of the 52-week low", "fall")
    except Exception as e:
        print(f"Error in is_close_to_52_week_low: {e}")



def is_close_to_52_week_high(high, ticker): # Changed to accept ticker
    """
    Checks if the current high is within 10% of the 52-week high and sends an alert.
    Args:
        high (float): The current day's high.
        ticker (yf.Ticker): The yfinance Ticker object.

    """
    try:
        fifty_two_week_high = ticker.info['fiftyTwoWeekHigh']
        percentage_difference = fifty_two_week_high - fifty_two_week_high * 0.10 # Corrected percentage calculation
        if high >= percentage_difference:
            send_telegram_alert("Nifty is within 10% of the 52-week high", "rise")
    except Exception as e:
        print(f"Error in is_close_to_52_week_high: {e}")

if __name__ == "__main__":
    today = datetime.date.today()
    if today.weekday() < 5:  # Changed to 5 for Monday to Friday (0-4)
        check_nifty_alerts()
    else:
        print("Today is not a trading day (Saturday or Sunday).")

def send_to_telegram(message):

    apiToken = '8017759392:AAEwM-W-y83lLXTjlPl8sC_aBmizuIrFXnU'
    chatID = '711856868'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

send_to_telegram("Hello from Python!")
