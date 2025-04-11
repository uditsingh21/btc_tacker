import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Step 1: Fetch news
def get_btc_news():
    url = (
        f"https://newsapi.org/v2/everything?q=bitcoin&sortBy=publishedAt&pageSize=10&apiKey={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    articles = data.get("articles", [])
    headlines = [article["title"] for article in articles]
    return headlines

# Step 2: Analyze sentiment
def analyze_sentiment(headlines):
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(h)["compound"] for h in headlines]
    avg_score = sum(scores) / len(scores) if scores else 0
    return avg_score, scores

#email alert!!

def send_sentiment_email(subject, message):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    receiver_email = os.getenv("EMAIL_TO")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("📬 Email alert sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)


# Run it
if __name__ == "__main__":
    headlines = get_btc_news()
    avg_score, scores = analyze_sentiment(headlines)

    print("\n📰 Headlines:")
    for i, headline in enumerate(headlines):
        print(f"{i+1}. {headline} (Score: {scores[i]:.2f})")

    print(f"\n📉 Average Sentiment Score: {avg_score:.2f}")

    if avg_score < -0.3:
        print("⚠️ ALERT: Sentiment is negative. Consider checking the market.")
        subject = "🚨 Bitcoin News Sentiment Alert"
        message = f"Sentiment Score: {avg_score:.2f}\n\n" + "\n".join(headlines)
        send_sentiment_email(subject, message)
    else:
        print("✅ Sentiment looks normal.")
