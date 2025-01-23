import os

from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
NAME_FROM = os.getenv("NAME_FROM")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_HASTAG = os.getenv("TG_HASTAG")
TG_HASTAG_ALL = os.getenv("TG_HASTAG_ALL")

DASHAMAIL_API_KEY = os.getenv("DASHAMAIL_API_KEY")
DASHAMAIL_LIST_ID = os.getenv("DASHAMAIL_LIST_ID")
DASHAMAIL_LIST_ALL_ID = os.getenv("DASHAMAIL_LIST_ALL_ID")
