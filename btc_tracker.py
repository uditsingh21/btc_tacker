import requests
import pandas as pd
from email.mime.text import MIMEText
from datetime import datetime
import smtplib
import os
from dotenv import load_dotenv

#loading the email credentials
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


#investment details

investment_inr = 5000
btc_buy_price_inr = 7219750  # INR at time of purchase
btc_amount = investment_inr / btc_buy_price_inr  # ~0.0006925 BTC
profit_target_pct = 25

#api (coingecko)

def fetch_btc_price_inr():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=inr"
    response = requests.get(url)
    data = response.json()
    return data["bitcoin"]["inr"]


#email alert

def send_email_alert(current_value, profit_pct):
    load_dotenv()
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    TO_EMAIL = os.getenv("TO_EMAIL")

    subject = "🚨 Bitcoin Profit Alert!"
    body = f"🎉 Your BTC investment has reached a profit of {profit_pct:.2f}%!\n\nCurrent Value: ₹{current_value:,.2f}"

    msg = MIMEText(body, _charset='utf-8')
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())

    print("📧 Email alert sent!")

#log to csv


def log_price(price_inr, value_inr, profit_pct):
    df = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "btc_price_inr": price_inr,
        "value_inr": value_inr,
        "profit_percent": profit_pct
    }])

    file_exists = os.path.isfile("btc_price_log.csv")
    df.to_csv("btc_price_log.csv", mode='a', header=not file_exists, index=False)


# main tracker


def main():
    btc_price_inr = fetch_btc_price_inr()
    current_value = btc_amount * btc_price_inr
    profit_pct = ((current_value - investment_inr) / investment_inr) * 100

    print(f"💹 BTC Price: ₹{btc_price_inr}")
    print(f"💰 Current Value: ₹{current_value:.2f} ({profit_pct:.2f}%)")

    log_price(btc_price_inr, current_value, profit_pct)

    if profit_pct >= profit_target_pct:
        send_email_alert(current_value, profit_pct)


if __name__ == "__main__":
    main()