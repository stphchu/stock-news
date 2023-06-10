import os
from dotenv import load_dotenv
import requests
from datetime import date
from datetime import timedelta
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
PERCENT_THRESHOLD = 5

load_dotenv("venv/.env")
alphav_api_key = os.getenv("STOCK_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(twilio_account_sid, twilio_auth_token)
twilio_number = os.getenv("TWILIO_NUM")
to_sms_number = os.getenv("TO_NUMBER")

current_date = date.today()
yesterday_date = str(current_date - timedelta(days=1))
day_before_date = str(current_date - timedelta(days=2))

stock_url = "https://www.alphavantage.co/query?"
stock_params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": alphav_api_key,
}

stock_response = requests.get(url=stock_url, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()
prev_close = float(stock_data["Time Series (Daily)"][day_before_date]["4. close"])
yesterday_close = float(stock_data["Time Series (Daily)"][yesterday_date]["4. close"])
price_change_percent = ((prev_close - yesterday_close) / prev_close) * 100

if price_change_percent < 0:
    change_icon = "🔻"
else:
    change_icon = "🔺"

if abs(price_change_percent) >= PERCENT_THRESHOLD:
    news_url = "https://newsapi.org/v2/everything?"
    news_params = {
        "q": COMPANY_NAME,
        "apiKey": news_api_key,
    }
    news_response = requests.get(url=news_url, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()
    articles = news_data["articles"][:3]

    summary_msgs = [f"{STOCK}: {change_icon} {abs(price_change_percent):.2f}%\n\n"
                    f"Headline: \n{article['title']}\n\n"
                    f"Brief: \n{article['description']}\n\n"
                    f"{article['url']}"
                    for article in articles]

    for msg in summary_msgs:
        message = client.messages.create(
            body=f"{msg}",
            from_=twilio_number,
            to=to_sms_number
        )