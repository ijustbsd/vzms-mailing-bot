import os

from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_HASTAG = os.getenv("TG_HASTAG")

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
